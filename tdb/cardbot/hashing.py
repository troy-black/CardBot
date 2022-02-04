import logging
import time
from typing import List

import imagehash
from sqlalchemy.orm import Session

from tdb.cardbot.crud.card import Card


class HashRow:
    uuid: str
    record_hash: str
    image_hash: imagehash.ImageHash

    def __init__(self, uuid: str, record_hash: str):
        """
        Holds phash details
            image_hash: ImageHash

        :param uuid: MTGJson uuid
        :param record_hash: phash str as stored in DB Record
        """
        self.uuid = uuid
        self.record_hash = record_hash
        self.image_hash = imagehash.hex_to_hash(record_hash)


class HashTable:
    rows: List[HashRow] = []

    def __init__(self, db: Session):
        """
        Holds a List[HashRow] and ways to compare phash

        :param db: SqlAlchemy DB Session
        """
        records: List[Card] = Card.read_all_hashes(db)

        self.rows = [
            HashRow(r.uuid, r.phash_32)
            for r in records
        ]

    def get_closest_match(self, image_hash: imagehash.ImageHash) -> str:
        """
        Find the nearest neighbor phash using hamming distance

        :param image_hash: ImageHash object
        :return: phash str as stored in DB Record
        """
        logging.debug(f'Calculating Hamming Diffs {image_hash}')
        t = time.time() if logging.root.level == logging.DEBUG else 0

        hamming_diffs = {
            row.uuid: row.image_hash - image_hash
            for row in self.rows
        }

        closest_key = min(hamming_diffs, key=hamming_diffs.get)
        closest_val = min(hamming_diffs.values())

        logging.debug(f'Calculated Hamming Diffs Complete {time.time() - t} key:{closest_key} val:{closest_val}')

        return closest_key
