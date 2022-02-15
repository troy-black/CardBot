import logging
from abc import ABC

from fastapi import FastAPI, APIRouter
from uvicorn import Config as UvicornConfig
from uvicorn import Server

from tdb.cardbot import config
from tdb.cardbot import logger
from tdb.cardbot.routes import BaseRoutes


class BaseApp(ABC):
    app: FastAPI = FastAPI()

    router: APIRouter
    config: config.BaseConfig

    @classmethod
    def launch(cls):
        # TODO - pass cmd args here...
        cls.config.load()

        logging.debug(f'Starting Application')

        cls.app.include_router(BaseRoutes.router)

        # Load specific api routes for application
        cls.app.include_router(cls.router)

        uvicorn_config = UvicornConfig(
            cls.app,
            host='0.0.0.0',
            log_level=cls.config.log_level.lower(),
            workers=4
        )

        server = Server(uvicorn_config)

        # override logging settings to all use loguru
        logger.setup_logging(cls.config.log_level, cls.config.serialize_logging)

        # Call any specific application setup
        cls._setup()

        server.run()

    @classmethod
    def _setup(cls):
        # Optional setup steps
        pass
