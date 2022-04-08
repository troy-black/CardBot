from typing import TypeVar, Callable, List

from sqlalchemy import Column
from sqlalchemy.engine import Row
from sqlalchemy.orm import Session

from tdb.cardbot import crud
from tdb.cardbot.core import schemas, models


class Card(crud.CRUD):
    Schema = TypeVar('Schema', bound=schemas.Card)
    Model = TypeVar('Model', bound=models.Card)

    model_class: Callable = models.Card
    model_column: Column = models.Card.id

    id: str

    @classmethod
    def new_read_all_hashes(cls, db: Session, offset: int = 0, limit: int = 100) -> List[Row]:
        return db.query(
            models.Card.id,
            models.Card.phash_32,
        ).filter(
            models.Card.phash_32.is_not(None)
        ).offset(offset).limit(limit).all()


class CardMeta(crud.CRUD):
    Schema = TypeVar('Schema', bound=schemas.CardMeta)
    Model = TypeVar('Model', bound=models.CardMeta)

    model_class: Callable = models.CardMeta
    model_column: Column = models.CardMeta.id


class CardHistoricPricing(crud.CRUD):
    Schema = TypeVar('Schema', bound=schemas.CardHistoricPricing)
    Model = TypeVar('Model', bound=models.CardHistoricPricing)

    model_class: Callable = models.CardHistoricPricing
    model_column: Column = models.CardHistoricPricing.id
