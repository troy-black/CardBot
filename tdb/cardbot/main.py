from uvicorn import Config as UvicornConfig
from uvicorn import Server

from tdb.cardbot import logger
from tdb.cardbot import database


def main():
    uvicorn_config = UvicornConfig(
        'tdb.cardbot.app:app',
        host='0.0.0.0',
        log_level='debug',
    )

    server = Server(uvicorn_config)

    # override logging settings to all use loguru
    logger.setup_logging('DEBUG', False)

    server.run()


if __name__ == '__main__':
    main()
