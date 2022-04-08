from sqlalchemy.orm import Session

from tdb.cardbot.crud import job


class Job(job.Job):
    @classmethod
    def truncate(cls, db: Session):
        """
        Delete all records from Table

        :param db: SqlAlchemy DB Session
        """

        db.execute(f'TRUNCATE TABLE {cls.model_class.__tablename__} restart identity')

        db.commit()
