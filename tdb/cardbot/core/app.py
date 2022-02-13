from fastapi import APIRouter

from tdb.cardbot.app import BaseApp
from tdb.cardbot.core import routes
from tdb.cardbot.core.database import Database


class App(BaseApp):
    router: APIRouter = routes.router

    @classmethod
    def _setup(cls):
        # Bind DB Model Object to each DB Table
        Database.base.metadata.create_all(bind=Database.engine())
