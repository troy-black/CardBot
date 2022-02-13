from typing import TypeVar, Callable, Union

from sqlalchemy import Column
from sqlalchemy.orm import Session

from tdb.cardbot.core import schemas, models
from tdb.cardbot.core.crud import CRUD


class Job(CRUD):
    Schema = TypeVar('Schema', bound=schemas.JobDetails)
    Model = TypeVar('Model', bound=models.Job)

    model_class: Callable = models.Job
    model_column: Column = models.Job.job_id

    @classmethod
    def read_one(cls, db: Session, key: Union[int, str]) -> Model:
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
