from fastapi import APIRouter

from tdb.cardbot import app
from tdb.cardbot.core import config, database, hashing, routes
from tdb.cardbot.crud.job import Job


class App(app.BaseApp):
    router: APIRouter = routes.Routes.router
    config = config.CoreConfig

    @classmethod
    def _setup(cls):
        # Bind DB Model Object to each DB Table
        database.Database.base.metadata.create_all(bind=database.Database.engine())

        # Clear temp table(s)
        with database.Database.db_contextmanager() as db:
            Job.truncate(db)

        hashing.HashTable.load()


if __name__ == '__main__':
    App.launch()
