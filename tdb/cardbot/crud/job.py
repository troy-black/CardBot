from typing import TypeVar, Callable, Union

import sqlalchemy
from sqlalchemy import orm

from tdb.cardbot import crud
from tdb.cardbot import models, schemas


class Job(crud.CRUD):
    Schema = TypeVar('Schema', bound=schemas.JobDetails)
    Model = TypeVar('Model', bound=models.Job)

    model_class: Callable = models.Job
    model_column: sqlalchemy.Column = models.Job.job_id

    @classmethod
    def read_one(cls, db: orm.Session, key: Union[int, str]) -> Model:
        """
        Read the matching record based on unique key

        :param db: SqlAlchemy DB Session
        :param key: Unique key for record identity
        :return: DB Model Record
        """
        if isinstance(key, int):
            return db.query(cls.model_class).filter(cls.model_column == key).first()
        else:
            return db.query(cls.model_class) \
                .filter(models.Job.job_type == key) \
                .order_by(cls.model_column.desc()) \
                .first()
