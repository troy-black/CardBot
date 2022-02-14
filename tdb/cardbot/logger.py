import logging
import sys

from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record):
        """
        Custom logging Handler to homogenize all logs

        :param record: logging record
        """
        # Get corresponding loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging(level: str, serialize: bool):
    """
    Set logging defaults across all modules

    :param level: Logging level to set all handlers
    :param serialize: Should logs be serialized beforehand
    """
    # intercept everything at the root logger
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(level)

    # remove every other logger's handlers
    # and propagate to root logger
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    # TODO - Does this need removed from 'node'
    # Change specific loggers to lower log noise
    logging.getLogger('PIL.PngImagePlugin').setLevel(logging.WARNING)

    # configure loguru
    logger.configure(handlers=[
        {
            'sink': sys.stdout,
            'serialize': serialize,
            'format': '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | '
            # '<cyan>{process.name: <10}</cyan> | '
                      '<level>{level: <8}</level> | '
                      '<cyan>{thread.name: <10}</cyan> | '
                      '<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>'
        }
    ])
