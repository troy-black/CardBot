from abc import ABC

from uvicorn import Config as UvicornConfig
from uvicorn import Server
from uvicorn.importer import import_from_string

from tdb.cardbot.app import BaseApp
from tdb.cardbot import logger, config


class BaseMain(ABC):
    # app: BaseApp
    config: config.BaseConfig

    @classmethod
    def launch(cls):
        # TODO - pass cmd args here...
        cls.config.load()

        app = import_from_string(cls.config.app)

        app.setup()

        uvicorn_config = UvicornConfig(
            app.app(),
            # cls.config.app,
            host='0.0.0.0',
            log_level=cls.config.log_level.lower(),
            workers=4
        )

        server = Server(uvicorn_config)

        # override logging settings to all use loguru
        logger.setup_logging(cls.config.log_level, cls.config.serialize_logging)

        cls._setup()

        server.run()

    @classmethod
    def _setup(cls):
        # Optional setup steps
        pass
