from typing import TypeVar, Callable

from sqlalchemy import Column
from sqlalchemy.orm import Session

from tdb.cardbot import models, schemas
from tdb.cardbot.crud import CRUD


class Card(CRUD):
    Schema = TypeVar('Schema', bound=schemas.CardFull)
    Model = TypeVar('Model', bound=models.Card)

    model_class: Callable = models.Card
    model_column: Column = models.Card.uuid

    @classmethod
    def read_one_by_scryfall_and_name(cls, db: Session, scryfall_id: str, card_name: str) -> models.Card:
        return db.query(models.Card).filter(
            models.Card.scryfallId == scryfall_id
            and models.Card.searchName == card_name
        ).first()
