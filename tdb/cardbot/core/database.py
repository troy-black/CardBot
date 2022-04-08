import os

from sqlalchemy import create_engine

from tdb.cardbot import database


class Database(database.BaseDatabase):
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
                max_overflow=os.cpu_count() + 4,
                # echo='debug'
            )

        return cls._engine

    @classmethod
    def truncate(cls, tablename: str) -> str:
        return f'TRUNCATE TABLE {tablename} restart identity'
