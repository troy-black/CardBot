import contextlib

import sqlalchemy
from sqlalchemy import orm
from sqlalchemy.ext import declarative


class BaseDatabase:
    _engine = None
    _local_session = None
    base = declarative.declarative_base()

    @classmethod
    def engine(cls) -> sqlalchemy.create_engine:
        ...

    @classmethod
    def truncate(cls, tablename: str):
        ...

    @classmethod
    def local_session(cls) -> orm.sessionmaker:
        """
        Create DB Session

        :return: DB Session
        """
        # Lazy load DB session maker
        if not cls._local_session:
            cls._local_session = orm.sessionmaker(autocommit=False, autoflush=False, bind=cls.engine())

        return cls._local_session

    @classmethod
    def get_db(cls):
        db = cls.local_session()()
        try:
            yield db
        finally:
            if db.bind.engine.url[0] != 'sqlite':
                db.close()

    @classmethod
    @contextlib.contextmanager
    def db_contextmanager(cls) -> orm.Session:
        """
        DB Context Manager
        """
        db = cls.local_session()()
        try:
            yield db
        # except Exception as e:
        #     # rollback session
        finally:
            db.close()
