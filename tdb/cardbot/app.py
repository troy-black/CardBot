import logging
from abc import ABC

from fastapi import FastAPI, APIRouter


class BaseApp(ABC):
    _app: FastAPI = None
    router: APIRouter

    @classmethod
    def app(cls):
        # Lazy Load FastApi Service
        if not cls._app:
            cls._app = FastAPI()
        return cls._app

    @classmethod
    def setup(cls):
        logging.debug('Starting Application')

        # Call any specific application setup
        cls._setup()

        # Load specific api routes for application
        cls.app().include_router(cls.router)

    @classmethod
    def _setup(cls):
        # Optional setup steps
        pass
