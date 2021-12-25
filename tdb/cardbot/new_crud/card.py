from typing import TypeVar, Callable

from sqlalchemy import Column

from tdb.cardbot import models, schemas
from tdb.cardbot.new_crud import CRUD


class Card(CRUD):
    Schema = TypeVar('Schema', bound=schemas.CardFull)
    Model = TypeVar('Model', bound=models.Card)
    # Key = TypeVar('Key', bound=str)

    model_class: Callable = models.Card
    model_column: Column = models.Card.uuid
