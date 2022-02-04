import json
import os
from pathlib import Path


class Config:
    hash_pixels_height: int = 1000
    image_path: str = '/images/'
    log_level: str = 'DEBUG'
    max_threads: int = 1

    serialize_logging: bool = False

    @classmethod
    def load(cls, **kwargs):
        """
        Build new Global Config object. Starts with any passed kwargs and updates records from any config.json file.

        Example: dict(
            hash_pixels_height=1000,
            image_path='/images/',
            log_level='DEBUG',
            max_threads=1
        )

        :param kwargs: Dictionary of items to build the Config object from
        """
        # Load kwargs as base
        details = kwargs or {}
        filename = kwargs.get('config', 'config.json')

        # Check for a config.json file
        if os.path.exists(filename):
            with open(filename, 'r') as json_file:
                result = json.load(json_file)

                # Update results from config.json with kwargs
                if isinstance(result, dict):
                    result.update(details)
                    details = result

        # Load base image_path
        if details.get('image_path'):
            cls.image_path = details.get('image_path')
        else:
            # Set default to 2 parents from the app ('../../images/')
            from tdb.cardbot import app
            parent_path = Path(os.path.abspath(app.__file__)).parents[2]
            cls.image_path = f'{parent_path}/images/'
        os.makedirs(cls.image_path, exist_ok=True)

        # Load remaining Config details
        cls.hash_pixels_height = details.get('hash_pixels_height', cls.hash_pixels_height)
        cls.log_level = details.get('log_level', cls.log_level)
        cls.max_threads = details.get('max_threads', os.cpu_count() or cls.max_threads)
        cls.serialize_logging = details.get('serialize_logging', cls.serialize_logging)
