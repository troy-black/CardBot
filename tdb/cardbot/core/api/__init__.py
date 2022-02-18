import datetime
import logging
from pathlib import Path
from typing import List

from sqlalchemy.orm import Session

from tdb.cardbot.core import config
from tdb.cardbot.core.api.mtgjson import MTGJson, Filenames
from tdb.cardbot.core.api.scryfall import Scryfall
from tdb.cardbot.core.crud.card import Card
from tdb.cardbot.core.crud.job import Job
from tdb.cardbot.core.crud.set import Set
from tdb.cardbot.core.database import Database
from tdb.cardbot.core.schemas import SetFull, JobDetails, NewCard
from tdb.cardbot.futures import Thread, ThreadPool, JobPool


class Api(JobPool):
    @classmethod
    def _process_card(cls, db: Session, card_data: dict, scryfall_data: dict, pricing: dict):
        """
        Update DB with a Card's info. Download Image from Scryfall and build phash for the Image

        :param db: DB Session
        :param card_data: Dict of individual card data
        :param scryfall_data: Dict of Scryfall Api image URL keyed by (ScryfallId, CardName)
        :param pricing: dict containing pricing data from mtgjson
        """
        scryfall_id = card_data.get('identifiers', {}).get('scryfallId')

        # Lookup image url from scryfall_data keyed by scryfall_id, name
        png_url = scryfall_data.get((scryfall_id, card_data.get('faceName') or card_data['name']))
        image_local = str(Path(card_data.get('setCode'), f'{scryfall_id}.png')) if png_url else None

        prices = {
            f'{store}_{list_type}_{card_type}': card_prices
            for store, store_vals in (pricing or {}).items()
            for list_type, card_types in (store_vals or {}).items()
            if isinstance(card_types, dict)
            for card_type, card_prices in (card_types or {}).items()
        }

        card_full = NewCard(
            **card_data,
            scryfallId=scryfall_id,
            imageUrl=png_url,
            imageLocal=image_local,
            **prices
        )

        card = Card.upsert(db, card_full, commit=False)

        card.download_image()

    @classmethod
    def _process_set(cls, db: Session, set_data: dict, scryfall_data: dict, prices: dict) -> int:
        """
        Update DB with a Card Set's info.

        :param db: DB Session
        :param set_data: Dict of mtg card set
        :param scryfall_data: Dict of Scryfall Api image URL keyed by (ScryfallId, CardName)
        :param prices: dict containing pricing data from mtgjson
        :return: Count of new/updated records
        """
        set_full = SetFull(**set_data)
        Set.upsert(db, set_full)

        cards = set_data['cards']

        count = 0
        card_count = len(cards)
        uuids = []

        for card_data in cards:

            # MTGJson results can include duplicate uuids.
            if card_data['uuid'] not in uuids:
                uuids.append(card_data['uuid'])

                paper = prices.get(card_data['uuid'], {}).get('paper')

                cls._process_card(db, card_data, scryfall_data, paper)

                count += 1

                logging.debug(f'Processed Card: [{card_data["setCode"]}] {card_data["name"]} '
                              f'{count} of {card_count} - {round((count / card_count) * 100, 2)}%')

        return count

    @classmethod
    def _update_database_thread(cls, mtgjson_data: list[dict], scryfall_data: dict, prices: dict, job_id: str) -> dict:
        """
        Separate thread to process shared mtgjson_data

        :param mtgjson_data: List[dict] containing complete card data by card set
        :param scryfall_data: dict containing Scryfall Api Image URL info keyed by scryfallId and cardName
        :param prices: dict containing pricing data from mtgjson
        :return: details on how many records were processed per set
        """
        results = {}

        # use a separate db connection for each thread
        with Database.db_contextmanager() as db:
            while mtgjson_data and Job.read_one(db, job_id).status == 'running':
                set_data = mtgjson_data.pop()

                results[set_data['code']] = cls._process_set(db, set_data, scryfall_data, prices)

                db.commit()

        return results

    @classmethod
    def _run(cls, details: JobDetails):
        """
        Download and process data from external API sources (MTGJson, Scryfall)

        :param details: Job details
        """
        logging.debug(f'Starting Api update_data: {details.job_id}')

        cls.last_job_id = details.job_id

        # Download data from Scryfall and MTGJson APIs (threaded)
        threads: List[Thread] = [
            Thread(Scryfall.download_data, results_id='scryfall'),
            Thread(MTGJson.download_data, results_id='mtgjson', filename=Filenames.ALL_PRINTINGS),
            Thread(MTGJson.download_prices, results_id='prices')
        ]
        results = ThreadPool.run(threads, thread_prefix='ApiSink')

        # Separate results
        prices = results.pop('prices')
        mtgjson_data = list(results.pop('mtgjson').values())
        scryfall_data = results.pop('scryfall')

        # Start a new ThreadPool to process the download data from external api
        threads: List[Thread] = [
            Thread(
                cls._update_database_thread,
                mtgjson_data=mtgjson_data,
                scryfall_data=scryfall_data,
                prices=prices,
                job_id=details.job_id
            )
            for _ in range(config.Config.max_threads)
        ]
        results = ThreadPool.run(threads, thread_prefix='GetCard')

        with Database.db_contextmanager() as db:
            # Refresh details
            details = Job.read_one(db, details.job_id)

            details.results = results

            if details.status == 'running':
                details.status = 'complete'

            details.end_time = datetime.datetime.now()

            db.commit()

            logging.debug(f'Completed Api update_data: {details.job_id}')

        cls._lock.release()
