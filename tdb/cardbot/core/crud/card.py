from typing import TypeVar, Callable, List

from sqlalchemy import Column
from sqlalchemy.orm import Session

from tdb.cardbot.core import schemas, models
from tdb.cardbot.core.crud import CRUD


class Card(CRUD):
    Schema = TypeVar('Schema', bound=schemas.CardFull)
    Model = TypeVar('Model', bound=models.Card)

    model_class: Callable = models.Card
    model_column: Column = models.Card.id

    id: str
    phash_32: str
    set: str
    scryfall_id: str
    image_url: str
    image_local: str

    @classmethod
    def read_all_hashes(cls, db: Session) -> List[models.Card]:
        """
        Pull all records with a phash

        :param db: SqlAlchemy DB Session
        :return: List[Card]
        """
        return db.query(models.Card).filter(
            models.Card.phash_32 is not None
        ).all()
