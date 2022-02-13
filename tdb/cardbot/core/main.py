from tdb.cardbot.config import BaseConfig
from tdb.cardbot.core import config
from tdb.cardbot.core.crud.job import Job
from tdb.cardbot.core.crud.log import Log
from tdb.cardbot.core.database import Database
from tdb.cardbot.main import BaseMain


class Main(BaseMain):
    config: BaseConfig = config.Config

    @classmethod
    def _setup(cls):
        with Database.db_contextmanager() as db:
            Log.truncate(db)
            Job.truncate(db)


if __name__ == '__main__':
    Main.launch()
