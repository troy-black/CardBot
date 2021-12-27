from typing import TypeVar, Callable

from sqlalchemy import Column

from tdb.cardbot import models, schemas
from tdb.cardbot.crud import CRUD


class Set(CRUD):
    Schema = TypeVar('Schema', bound=schemas.SetFull)
    Model = TypeVar('Model', bound=models.Set)

    model_class: Callable = models.Set
    model_column: Column = models.Set.code
