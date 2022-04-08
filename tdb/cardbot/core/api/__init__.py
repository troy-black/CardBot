import datetime
import logging
import os
import re
from pathlib import Path
from typing import List, Union, Optional

from sqlalchemy.orm import Session

from tdb.cardbot import futures
from tdb.cardbot import schemas as base_schemas
from tdb.cardbot.core import config
from tdb.cardbot.core import database
from tdb.cardbot.core import hashing, models
from tdb.cardbot.core import schemas
from tdb.cardbot.core import utils
from tdb.cardbot.core.api import mtgjson
from tdb.cardbot.core.api import scryfall
from tdb.cardbot.core.crud import card
from tdb.cardbot.crud import job


class Api(futures.JobPool):
    _database = database.Database

    @classmethod
    def download_image(cls, image_url: str, image_local: str):
        """
        Download image from Scryfall Api
        """
        filepath = Path(config.CoreConfig.image_path, image_local)
        filename = str(filepath)

        if not os.path.exists(filename):
            utils.download_file(url=image_url, filename=filename)
            return True

        return False

    @classmethod
    def _hash_image(cls, image_local: str, hash_size=32) -> hashing.HashImage:

        filepath = Path(config.CoreConfig.image_path, image_local)
        hash_image = hashing.HashImage(filepath, hash_size=hash_size)

        return hash_image

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

        new_card = schemas.Card(
            **card_data,
            object_type=card_data['object'],
            image_url=png_url,
            image_local=image_local
        )
        card_record: models.Card = card.Card.upsert(db, new_card, commit=False)

        card_data['prices'] = cls._cleanup_json(card_data.get('prices'))

        new_meta = schemas.CardMeta(**card_data)
        if new_meta.dict(exclude_unset=True, exclude_defaults=True, exclude={'id'}):
            card.CardMeta.upsert(db, new_meta, commit=False)

        if png_url:
            updated = cls.download_image(png_url, image_local)

            if not card_record.phash_32:
                try:
                    hash_image = cls._hash_image(image_local, 32)
                    card_record.phash_32 = str(hash_image.image_hash)
                    updated = True
                except Exception as e:
                    print(e)

            # if not card_record.phash_48:
            #     try:
            #         hash_image = cls._hash_image(image_local, 48)
            #         card_record.phash_48 = str(hash_image.image_hash)
            #         updated = True
            #     except Exception as e:
            #         print(e)
            #
            # if not card_record.phash_64:
            #     try:
            #         hash_image = cls._hash_image(image_local, 64)
            #         card_record.phash_64 = str(hash_image.image_hash)
            #         updated = True
            #     except Exception as e:
            #         print(e)

        db.commit()

    @classmethod
    def _get_card_data(cls, scryfall_data: List[dict]):
        try:
            return scryfall_data.pop()
        except IndexError:
            return None

    @classmethod
    def _cleanup_json(cls, json: Optional[Union[dict, list]]) -> Optional[Union[dict, list]]:
        if not json or str(json).lower() == 'null':
            return None

        if isinstance(json, dict):
            for key in [key
                        for key, val in json.items()
                        if not val or str(val).lower() == 'null']:
                json[key] = None

            if all(not v for v in json.values()):
                return None

        return json

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
        with database.Database.db_contextmanager() as db:
            while scryfall_data:
                card_data = cls._get_card_data(scryfall_data)

                if not card_data:
                    break

                scryfall_id = card_data['id']
                lang = card_data['lang']
                card_set = card_data['set']

                card_faces = []
                for card_face in card_data.get('card_faces', {}):
                    # Found duplicate card face names in scryfall card_faces
                    name = card_face['name']
                    if name not in card_faces:
                        card_faces.append(name)
                        if 'image_status' not in card_face:
                            card_face['image_status'] = card_data.get('image_status')
                        cls._process_card(
                            db,
                            id=f'{scryfall_id}-{name}',
                            scryfall_id=scryfall_id,
                            lang=lang,
                            set=card_set,
                            **cls._cleanup_json(card_face)
                        )

                mtgjson_uuid = mtgjson_data.get(scryfall_id)

                cls._process_card(
                    db,
                    scryfall_id=scryfall_id,
                    mtgjson_uuid=mtgjson_uuid,
                    **cls._cleanup_json(card_data)
                )

                card_price_groups = cls._cleanup_json({
                    f'{store}_{list_type}_{card_type}': card_prices
                    for store, store_vals in prices.get(mtgjson_uuid, {}).get('paper', {}).items()
                    for list_type, card_types in (store_vals or {}).items()
                    if isinstance(card_types, dict)
                    for card_type, card_prices in (card_types or {}).items()
                })

                if card_price_groups:
                    new_historic = schemas.CardHistoricPricing(
                        id=card_data['id'],
                        **card_price_groups
                    )
                    card.CardHistoricPricing.upsert(db, new_historic, commit=True)

                if processed % 200:
                    db.commit()

                    if not job.Job.read_one(db, job_id).status == 'running':
                        print()
                        break

                logging.debug(f'Api Db Update - Remaining {len(scryfall_data)}')

            db.commit()

        return {'processed': processed}

    @classmethod
    def _run(cls, details: base_schemas.JobDetails):
        """
        Download and process data from external API sources (MTGJson, Scryfall)

        :param details: Job details
        """
        logging.debug(f'Starting Api update_data: {details.job_id}')

        cls.last_job_id = details.job_id

        # Download data from Scryfall and MTGJson APIs (threaded)
        threads: List[futures.Thread] = [
            futures.Thread(scryfall.Scryfall.download_data, results_id='scryfall'),
            futures.Thread(mtgjson.MTGJson.download_card_identifiers, results_id='mtgjson'),
            futures.Thread(mtgjson.MTGJson.download_prices, results_id='prices')
        ]
        results = futures.ThreadPool.run(threads, thread_prefix='ApiSink')

        # Separate results
        scryfall_data = results.pop('scryfall')
        mtgjson_data = results.pop('mtgjson')
        prices = results.pop('prices')

        # Start a new ThreadPool to process the download data from external api
        threads: List[futures.Thread] = [
            futures.Thread(
                cls._update_database_thread,
                mtgjson_data=mtgjson_data,
                scryfall_data=scryfall_data,
                prices=prices,
                job_id=details.job_id
            )
            for _ in range(config.CoreConfig.max_threads)
        ]
        results = futures.ThreadPool.run(threads, thread_prefix='GetCard')

        with database.Database.db_contextmanager() as db:
            # Refresh details
            details = job.Job.read_one(db, details.job_id)

            details.results = results

            if details.status == 'running':
                details.status = 'complete'

            details.end_time = datetime.datetime.now()

            db.commit()

            logging.debug(f'Completed Api update_data: {details.job_id}')

        cls._lock.release()
