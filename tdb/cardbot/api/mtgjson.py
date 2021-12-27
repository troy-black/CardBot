import logging
from enum import Enum

from sqlalchemy.orm import Session

from tdb.cardbot import utils
from tdb.cardbot.crud.card import Card
from tdb.cardbot.crud.set import Set
from tdb.cardbot.schemas import SetFull, CardFull

MTGJSON_API_URL = 'https://mtgjson.com/api/v5/'


class MTGJsonFiles(Enum):
    META = 'Meta.json'
    ALL = 'AllPrintings.json'


class MTGJson:
    COMPRESSION = '.xz'

    @classmethod
    def process(cls, enum: MTGJsonFiles) -> dict:
        filename = f'{enum.value}{cls.COMPRESSION}'
        data = utils.download_file(f'{MTGJSON_API_URL}{filename}')

        meta: dict = data['meta']
        logging.debug(f'Meta {enum}: {meta}')

        return data['data']

    @classmethod
    def process_all_printings(cls, db: Session):
        for set_data in cls.process(MTGJsonFiles.ALL).values():
            set_full = SetFull(**set_data)
            Set.upsert(db, set_full)

            for card_data in set_data['cards']:
                card_full = CardFull(
                    **card_data,
                    scryfallId=card_data.get('identifiers', {}).get('scryfallId')
                )
                Card.upsert(db, card_full, commit=False)

            db.commit()
