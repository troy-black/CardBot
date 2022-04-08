import asyncio
import base64
import io
import logging
import os
import pathlib
from typing import List

import requests

from tdb.cardbot import futures, schemas as base_schemas
from tdb.cardbot import image
from tdb.cardbot.node import camera, config, database, gpio, models
from tdb.cardbot.node import schemas
from tdb.cardbot.node.crud import scans


class Indexer(futures.JobPool):
    _database: database.Database = database.Database

    last_scan: int = -1

    last_match: image.Image

    running: bool = False

    @classmethod
    def _run(cls, details: base_schemas.JobDetails,
             stack_name: str, language: str,
             foil: bool, proxy: bool, altered: bool,
             event: asyncio.Event, image_store: image.ImageStore,
             save_original_images: bool = False):
        logging.debug('Running Indexer')

        cls.running = True

        filepath = None
        image_path = pathlib.Path(config.NodeConfig.image_path, stack_name)
        os.makedirs(image_path, exist_ok=True)

        with database.Database.db_contextmanager() as db:
            row = scans.CardScan.read_last_index_by_stack(db, stack_name)
            stack_index = row[0] if row else 0

        gpio.Gpio.setup(home_stacks=False, blocking=True)

        while cls.running:
            stack_index += 1
            if save_original_images:
                original_image_local = f'original_{stack_index:03}.jpg'
                filepath = pathlib.Path(image_path, original_image_local)

            camera.PiCameraDriver.capture(filepath)

            threads: List[futures.Thread] = [
                futures.Thread(gpio.Gpio.begin_loop, home=False),
                futures.Thread(cls.image_processing,
                               image_path=image_path,
                               stack_name=stack_name,
                               stack_index=stack_index,
                               event=event,
                               image_store=image_store,
                               language=language,
                               foil=foil,
                               proxy=proxy,
                               altered=altered,
                               ),
            ]
            futures.ThreadPool.run(threads, thread_prefix='Indexer')
            print()

        gpio.Gpio.setup(home_stacks=False, blocking=True)

        logging.debug('Exited Indexing Run Loop')

    @classmethod
    def image_processing(cls, image_path: pathlib.Path, stack_name: str, stack_index: int,
                         language: str, foil: bool, proxy: bool, altered: bool,
                         event: asyncio.Event, image_store: image.ImageStore):
        with database.Database.db_contextmanager() as db:
            card_scan = scans.CardScan.read_one_by_stack(db, stack_name, stack_index)

            processed_image: base_schemas.ProcessedImage = cls.process_image()

            if '00000000-0000-0000-0000-000000000000' in processed_image.closest_matches:
                logging.debug('Card Back Detected. Exiting.')
                cls.running = False

            cropped_image_local = f'processed_{stack_index:03}.jpg'
            filepath = pathlib.Path(image_path, cropped_image_local)

            cls.save_image(filepath, base64.b64decode(processed_image.process_image))

            scan_details = schemas.CardScanDetails(
                stack_name=stack_name,
                stack_index=stack_index,
                card_id=processed_image.closest_matches[0],
                closest_matches=processed_image.closest_matches,
                language=language,
                foil=foil,
                proxy=proxy,
                altered=altered
            )

            if card_scan:
                print()
            else:
                card_scan = scans.CardScan.create(db, scan_details)

            image_store.img = image.Image(io.BytesIO(base64.b64decode(processed_image.matched_image)))

            ls = cls.last_scan

            cls.last_scan = ls + 1

            event.set()
            event.clear()

            return card_scan

    @classmethod
    async def get_event_image(cls, event: asyncio.Event, image_store: image.ImageStore):
        await event.wait()
        return image_store.img.modified_image

    @classmethod
    def process_image(cls) -> base_schemas.ProcessedImage:
        try:
            files = {'file': camera.PiCameraDriver.last_image_bytes}
            response = requests.post(
                f'{config.NodeConfig.core_url}/process/image',
                files=files
            )

            if response.status_code == 200:
                results = base_schemas.ProcessedImage(**response.json())
                return results
            else:
                print()
        except Exception as e:
            print(e)

    @classmethod
    def save_image(cls, filepath: pathlib.Path, filebytes: bytes):
        with open(filepath, 'wb') as out_file:
            out_file.write(filebytes)
