import datetime
import logging
import os
import re
from pathlib import Path
from typing import List

from sqlalchemy.orm import Session

from tdb.cardbot.core import config
from tdb.cardbot.core.api.mtgjson import MTGJson, Filenames
from tdb.cardbot.core.api.scryfall import Scryfall
from tdb.cardbot.core.crud.card import Card
from tdb.cardbot.core.crud.job import Job
from tdb.cardbot.core.database import Database
from tdb.cardbot.core.futures import JobPool
from tdb.cardbot.core.schemas import JobDetails, NewCard
from tdb.cardbot.futures import Thread, ThreadPool


class Api(JobPool):
    @classmethod
    def _filename(cls, name: str, scryfall_id: str):
        name = name.replace(os.path.sep, '|')
        name = re.sub(r'[^A-Za-z0-9 |]+', '', name)
        return f'{name}[{scryfall_id}].png'

    @classmethod
    def _process_card(cls, db: Session, **card_data):
        png_url = None
        image_local = None

        if card_data.get('image_status', '') in ('highres_scan', 'lowres'):
            png_url = card_data.get('image_uris', {}).get('png')
            if png_url:
                name = cls._filename(card_data['name'], card_data['scryfall_id'])
                image_local = str(Path(
                    card_data['lang'],
                    card_data['set'],
                    name
                ))

        # TODO - Remove this....
        old_image_local = str(Path(
            card_data['lang'],
            card_data['set'],
            f"{card_data['scryfall_id']}-{card_data['name']}.png"
        ))
        old_filename = str(Path(config.Config.image_path, old_image_local))

        if png_url and image_local and image_local != old_image_local:
            new_filename = str(Path(config.Config.image_path, image_local))
            if os.path.exists(old_filename) and not os.path.exists(new_filename):
                os.replace(old_filename, new_filename)

        if os.path.exists(old_filename):
            os.remove(old_filename)
        # TODO - ................................................

        card_full = NewCard(
            **card_data,
            object_type=card_data['object'],
            image_url=png_url,
            image_local=image_local
        )

        card = Card.upsert(db, card_full, commit=False)

        if png_url:
            card.download_image()
        # TODO - Remove this.....
        else:
            if card.phash_32:
                card.phash_32 = None

    @classmethod
    def _get_card_data(cls, scryfall_data: List[dict]):
        try:
            return scryfall_data.pop()
        except IndexError:
            return None

    @classmethod
    def _update_database_thread(cls, mtgjson_data: dict, scryfall_data: List[dict], prices: dict, job_id: str) -> dict:
        """
        Separate thread to process shared mtgjson_data

        :param mtgjson_data: List[dict] containing complete card data by card set
        :param scryfall_data: dict containing Scryfall Api Image URL info keyed by scryfallId and cardName
        :param prices: dict containing pricing data from mtgjson
        :return: details on how many records were processed per set
        """
        processed = 0

        # use a separate db connection for each thread
        with Database.db_contextmanager() as db:
            while scryfall_data:
                card_data = cls._get_card_data(scryfall_data)

                if not card_data:
                    break

                scryfall_id = card_data['id']
                lang = card_data['lang']
                card_set = card_data['set']

                card_faces = []
                for card_face in card_data.get('card_faces', []):
                    # Found duplicate card face names in scryfall card_faces
                    name = card_face['name']
                    if name not in card_faces:
                        card_faces.append(name)
                        cls._process_card(
                            db,
                            id=f'{scryfall_id}-{name}',
                            scryfall_id=scryfall_id,
                            lang=lang,
                            set=card_set,
                            **card_face
                        )

                mtgjson_uuid = mtgjson_data.get(scryfall_id)

                card_price_groups = {
                    f'{store}_{list_type}_{card_type}': card_prices
                    for store, store_vals in prices.get(mtgjson_uuid, {}).items()
                    for list_type, card_types in (store_vals or {}).items()
                    if isinstance(card_types, dict)
                    for card_type, card_prices in (card_types or {}).items()
                }

                cls._process_card(
                    db,
                    scryfall_id=scryfall_id,
                    mtgjson_uuid=mtgjson_uuid,
                    **card_data,
                    **card_price_groups
                )

                if processed % 200:
                    db.commit()

                    if not Job.read_one(db, job_id).status == 'running':
                        break

                logging.debug(f'Api Db Update - Remaining {len(scryfall_data)}')

            db.commit()

        return {'processed': processed}

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
            Thread(MTGJson.download_card_identifiers, results_id='mtgjson'),
            Thread(MTGJson.download_prices, results_id='prices')
        ]
        results = ThreadPool.run(threads, thread_prefix='ApiSink')

        # Separate results
        scryfall_data = results.pop('scryfall')
        mtgjson_data = results.pop('mtgjson')
        prices = results.pop('prices')

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
