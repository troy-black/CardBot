import json
import os
from abc import ABC


class BaseConfig(ABC):
    app: str
    log_level: str = 'DEBUG'
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

        cls.log_level = details.get('log_level', cls.log_level)
        cls.serialize_logging = details.get('serialize_logging', cls.serialize_logging)

        cls._load(details)

    @classmethod
    def _load(cls, details: dict):
        # Optional setup steps
        pass
