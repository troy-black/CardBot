from typing import TypeVar, Callable, List

import sqlalchemy
from sqlalchemy import orm, func
from sqlalchemy.engine import Row

from tdb.cardbot import crud
from tdb.cardbot.node import models, schemas


class CardScan(crud.CRUD):
    Schema = TypeVar('Schema', bound=schemas.CardScanDetails)
    Model = TypeVar('Model', bound=models.CardScan)

    model_class: Callable = models.CardScan
    model_column: sqlalchemy.Column = models.CardScan.scan_id

    @classmethod
    def read_one_by_stack(cls, db: orm.Session, stack_name: str, stack_index: int) -> Model:
        return db.query(models.CardScan).filter(sqlalchemy.and_(
            models.CardScan.stack_name == stack_name,
            models.CardScan.stack_index == stack_index,
        )).first()

    @classmethod
    def read_stack_names(cls, db: orm.Session) -> List[Row]:
        return db.query(
            models.CardScan.stack_name
        ).group_by(
            models.CardScan.stack_name
        ).all()

    @classmethod
    def read_indexes_by_stack(cls, db: orm.Session, stack_name: str) -> Row:
        return db.query(
            models.CardScan.stack_index
        ).filter(
            models.CardScan.stack_name == stack_name
        ).order_by(
            models.CardScan.stack_index
        ).all()

    @classmethod
    def read_last_index_by_stack(cls, db: orm.Session, stack_name: str) -> Row:
        return db.query(
            func.max(models.CardScan.stack_index).label('maxIndex')
        ).filter(
            models.CardScan.stack_name == stack_name
        ).group_by(
            models.CardScan.stack_name
        ).first()
