from uvicorn import Config as UvicornConfig
from uvicorn import Server

from tdb.cardbot import config
from tdb.cardbot import logger
from tdb.cardbot.crud.job import Job
from tdb.cardbot.crud.log import Log
from tdb.cardbot.database import Database


def main():
    """
    Application entry point
    """
    # TODO - pass cmd args here...
    config.Config.load()

    uvicorn_config = UvicornConfig(
        'tdb.cardbot.app:app',
        host='0.0.0.0',
        log_level=config.Config.log_level.lower(),
        workers=4
    )

    server = Server(uvicorn_config)

    # override logging settings to all use loguru
    logger.setup_logging(config.Config.log_level, config.Config.serialize_logging)

    with Database.db_contextmanager() as db:
        Log.truncate(db)
        Job.truncate(db)

    server.run()


if __name__ == '__main__':
    main()
