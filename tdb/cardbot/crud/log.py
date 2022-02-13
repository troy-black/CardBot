from typing import TypeVar, Callable, List

from sqlalchemy import Column
from sqlalchemy.orm import Session

from tdb.cardbot import models, schemas
from tdb.cardbot.crud import CRUD


class Log(CRUD):
    Schema = TypeVar('Schema', bound=schemas.LogDetails)
    Model = TypeVar('Model', bound=models.Log)

    model_class: Callable = models.Log
    model_column: Column = models.Log.time

    @classmethod
    def read_logs(cls, db: Session, limit: int = 100) -> List[models.Log]:
        """
        Read all records from DB Table

        :param db: SqlAlchemy DB Session
        :param limit: Int - Place a limit on the number of returned records
        :return: List DB Model Record
        """
        results: List[models.Log] = db.query(cls.model_class).order_by(models.Log.log_id).limit(limit).all()

        for row in results:
            db.delete(row)

        db.commit()

        return results
