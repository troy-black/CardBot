import abc
import logging
from typing import TypeVar, Callable, List

import sqlalchemy
from sqlalchemy import orm

from tdb.cardbot import database
from tdb.cardbot import schemas


class CRUD(abc.ABC):
    Schema = TypeVar('Schema', bound=schemas.BaseSchema)
    Model = TypeVar('Model', bound=database.BaseDatabase.base)
    Key = TypeVar('Key', bound=str)

    model_class: Callable = None
    model_column: sqlalchemy.Column = None

    @classmethod
    def create(cls, db: orm.Session, schema: Schema, *, commit: bool = True) -> Model:
        """
        Create a new database record based on the Pydantic Schema

        :param db: SqlAlchemy DB Session
        :param schema: Pydantic Schema Object
        :param commit: Bool - Should this perform an immediate commit
        :return: DB Model Record
        """
        model = cls.model_class(**schema.dict())
        db.add(model)

        if commit:
            db.commit()
            db.refresh(model)

        if cls.__name__ != 'Log':
            logging.debug(f'Adding {cls.__name__}: {schema.dict()}')

        return model

    @classmethod
    def read_many(cls, db: orm.Session, offset: int = 0, limit: int = 100) -> List[Model]:
        """
        Read all records from DB Table

        :param db: SqlAlchemy DB Session
        :param offset: Int - Starting point to read records
        :param limit: Int - Place a limit on the number of returned records
        :return: List DB Model Record
        """
        return db.query(cls.model_class).offset(offset).limit(limit).all()

    @classmethod
    def read_one(cls, db: orm.Session, key: Key) -> Model:
        """
        Read the matching record based on unique key

        :param db: SqlAlchemy DB Session
        :param key: Unique key for record identity
        :return: DB Model Record
        """
        return db.query(cls.model_class).filter(cls.model_column == key).first()

    @classmethod
    def truncate(cls, db: orm.Session):
        """
        Delete all records from Table

        :param db: SqlAlchemy DB Session
        """

        # db.execute(f'TRUNCATE TABLE {cls.model_class.__tablename__} restart identity')
        db.execute(f'DELETE FROM {cls.model_class.__tablename__}')
        # db.execute(f'UPDATE sqlite_sequence SET seq = 0 WHERE name = {cls.model_class.__tablename__}')
        # UPDATE `sqlite_sequence` SET `seq` = 0 WHERE `name` = 'table_name';

        db.commit()
        print()

    @classmethod
    def upsert(cls, db: orm.Session, schema: Schema, *, commit: bool = True) -> Model:
        """
        Update existing record, or Insert a new record; based on the Pydantic Schema

        :param db: SqlAlchemy DB Session
        :param schema: Pydantic Schema Object
        :param commit: Bool - Should this perform an immediate commit
        :return: DB Model Record
        """

        # Check for existing record
        model: cls.model_class = cls.read_one(
            db=db,
            key=getattr(schema, cls.model_column.name)
        )

        if model:
            changes = {}

            # Update record and store changes
            for key, val in schema.dict(exclude_unset=True, exclude_defaults=True).items():
                old = getattr(model, key)
                if isinstance(old, dict):
                    # Merge dictionaries and sort
                    val = dict(sorted({**old, **(val or {})}.items()))

                if old != val:
                    setattr(model, key, val)
                    changes[key] = {
                        'new': val,
                        'old': old
                    }

            if changes:

                if commit:
                    db.commit()
                    db.refresh(model)

                logging.debug(f'Updating {schema.print()}: {changes}')

        else:
            # Create new record
            model = cls.create(db, schema, commit=commit)

        return model
