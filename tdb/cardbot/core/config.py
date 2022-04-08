import os
from pathlib import Path

from tdb.cardbot import config


class CoreConfig(config.BaseConfig):
    app: str = 'tdb.cardbot.core.app:App'
    image_path: str = '/images/'
    max_threads: int = 1

    phash_size: int = 32

    @classmethod
    def _load(cls, details: dict):
        # Load base image_path
        if details.get('image_path'):
            cls.image_path = details.get('image_path')
        else:
            # Set default to 2 parents from the base app ('../../images/')
            from tdb.cardbot import app
            parent_path = Path(os.path.abspath(app.__file__)).parents[2]
            cls.image_path = f'{parent_path}/images/'

        # Create path if it doesn't exist
        os.makedirs(cls.image_path, exist_ok=True)

        # Load remaining Core Config details
        cls.max_threads = details.get('max_threads', os.cpu_count() or cls.max_threads)
