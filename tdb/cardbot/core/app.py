from fastapi import APIRouter

from tdb.cardbot.app import BaseApp
from tdb.cardbot.core import config
from tdb.cardbot.core import routes
from tdb.cardbot.core.crud.job import Job
from tdb.cardbot.core.database import Database


class App(BaseApp):
    router: APIRouter = routes.router
    config = config.Config

    @classmethod
    def _setup(cls):
        # Bind DB Model Object to each DB Table
        Database.base.metadata.create_all(bind=Database.engine())

        # Clear temp table(s)
        with Database.db_contextmanager() as db:
            Job.truncate(db)


if __name__ == '__main__':
    App.launch()
