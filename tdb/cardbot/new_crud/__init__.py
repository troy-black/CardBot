import logging
from abc import ABC
from typing import List, TypeVar, Callable

from pydantic import BaseModel
from sqlalchemy import Column
from sqlalchemy.orm import Session

from tdb.cardbot.database import Base


class CRUD(ABC):
    Schema = TypeVar('Schema', bound=BaseModel)
    Model = TypeVar('Model', bound=Base)
    Key = TypeVar('Key', bound=str)

    model_class: Callable = None
    model_column: Column = None

    @classmethod
    def create(cls, db: Session, schema: Schema, *, commit: bool = True) -> Model:
        model = cls.model_class(**schema.dict())
        db.add(model)

        if commit:
            db.commit()
            db.refresh(model)

        return model

    @classmethod
    def read_one(cls, db: Session, key: Key) -> Model:
        return db.query(cls.model_class).filter(cls.model_column == key).first()

    @classmethod
    def read_many(cls, db: Session, skip: int = 0, limit: int = 100) -> List[Model]:
        return db.query(cls.model_class).offset(skip).limit(limit).all()

    @classmethod
    def upsert(cls, db: Session, schema: Schema) -> Model:
        changes = {}
        val = getattr(schema, cls.model_column.name)
        model: cls.model_class = cls.read_one(db, key=val)

        if model:
            for key, val in schema.dict().items():
                if hasattr(model, key) and getattr(model, key, 0) != val:
                    setattr(model, key, val)
                    changes[key] = val

            if changes:
                logging.debug(f'Updating {cls.__name__}: {changes}')

        else:
            model: cls.model_class = cls.model_class(**schema.dict())
            db.add(model)
            changes = True
            logging.debug(f'Adding {cls.__name__}: {schema.dict()}')

        if changes:
            db.commit()
            db.refresh(model)

        return model
