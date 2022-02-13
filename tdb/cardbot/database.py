import os
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session


class Database:
    _engine = None
    _local_session = None
    base = declarative_base()

    @classmethod
    def engine(cls) -> create_engine:
        """
        Create DB Connection

        :return: DB Engine
        """
        # Lazy load DB Connection
        if not cls._engine:
            cls._engine = create_engine(
                'postgresql://cardbot:cardbot@localhost:5432/cardbot',
                pool_size=os.cpu_count(),
                max_overflow=os.cpu_count() + 4
                # echo='debug'
            )

        return cls._engine

    @classmethod
    def local_session(cls) -> sessionmaker:
        """
        Create DB Session

        :return: DB Session
        """
        # Lazy load DB session maker
        if not cls._local_session:
            cls._local_session = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine())

        return cls._local_session

    @classmethod
    def get_db(cls):
        db = cls.local_session()()
        try:
            yield db
        finally:
            db.close()

    @classmethod
    @contextmanager
    def db_contextmanager(cls) -> Session:
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
