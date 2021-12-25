import logging

from enum import Enum
from sqlalchemy.orm import Session

from tdb.cardbot.new_crud.set import Set
from tdb.cardbot.new_crud.card import Card

from tdb.cardbot.schemas import SetFull, CardFull
from tdb.cardbot import utils
# from tdb.cardbot import old_crud as crud


MTGJSON_API_URL = 'https://mtgjson.com/api/v5/'


class MTGJsonFiles(Enum):
    META = 'Meta.json'
    ALL = 'AllPrintings.json'


class MTGJsonTables(Enum):
    ALL = {
        'a': 'a'
    }


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
    def download_meta(cls):
        cls.process(MTGJsonFiles.META)

    @classmethod
    def download_all_printings(cls, db: Session):
        data = cls.process(MTGJsonFiles.ALL)

        for _, set_data in data.items():
            set_full = SetFull(**set_data)
            Set.upsert(db, set_full)
            # crud.upsert_set(db=db, set_full=set_full)

            for card_data in set_data['cards']:
                card_full = CardFull(**card_data)
                Card.upsert(db, card_full)
                # crud.upsert_card(db=db, card_full=card_full)

        print()
