from typing import TypeVar, Callable

from sqlalchemy import Column

from tdb.cardbot.core import schemas, models
from tdb.cardbot.core.crud import CRUD


class Set(CRUD):
    Schema = TypeVar('Schema', bound=schemas.SetFull)
    Model = TypeVar('Model', bound=models.Set)

    model_class: Callable = models.Set
    model_column: Column = models.Set.code

    code: str
