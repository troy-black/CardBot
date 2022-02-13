from typing import TypeVar, Callable, List

from sqlalchemy import Column
from sqlalchemy.orm import Session

from tdb.cardbot import models, schemas
from tdb.cardbot.crud import CRUD


class Card(CRUD):
    Schema = TypeVar('Schema', bound=schemas.CardFull)
    Model = TypeVar('Model', bound=models.Card)

    model_class: Callable = models.Card
    model_column: Column = models.Card.uuid

    uuid: str
    phash_32: str
    setCode: str
    scryfallId: str
    imageUrl: str
    imageLocal: str

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
