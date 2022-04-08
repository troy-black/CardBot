import sqlalchemy

from tdb.cardbot import database


class Database(database.BaseDatabase):
    @classmethod
    def engine(cls) -> sqlalchemy.create_engine:
        """
        Create DB Connection

        :return: DB Engine
        """
        # Lazy load DB Connection
        if not cls._engine:
            cls._engine = sqlalchemy.create_engine('sqlite:///./app.db')

        return cls._engine
