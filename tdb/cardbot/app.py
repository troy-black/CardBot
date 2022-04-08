import abc
import logging
import pathlib

import fastapi
import uvicorn
from starlette import staticfiles

from tdb.cardbot import config, logger, routes


class BaseApp(abc.ABC):
    app: fastapi.FastAPI = fastapi.FastAPI()

    router: fastapi.APIRouter
    config: config.BaseConfig

    @classmethod
    def launch(cls):
        # TODO - pass cmd args here...
        cls.config.load()

        logging.debug(f'Starting Application')

        cls.app.include_router(routes.BaseRoutes.router)

        # Load specific api routes for application
        cls.app.include_router(cls.router)

        cls.app.mount('/static',
                      staticfiles.StaticFiles(
                          directory=str(pathlib.Path(str(pathlib.Path(__file__).parent), 'static'))),
                      name='static')

        uvicorn_config = uvicorn.Config(
            cls.app,
            host='0.0.0.0',
            log_level=cls.config.log_level.lower(),
            workers=4
        )

        server = uvicorn.Server(uvicorn_config)

        # override logging settings to all use loguru
        logger.setup_logging(cls.config.log_level, cls.config.serialize_logging)

        # Call any specific application setup
        cls._setup()

        server.run()

    @classmethod
    def _setup(cls):
        # Optional setup steps
        pass
