import json
import os
from pathlib import Path


class Config:
    image_path: str
    log_level: str = 'DEBUG'

    @classmethod
    def load(cls, **kwargs):
        details = kwargs or {}
        filename = kwargs.get('config', 'config.json')

        if os.path.exists(filename):
            with open(filename, 'r') as json_file:
                result = json.load(json_file)

                if isinstance(result, dict):
                    result.update(details)
                    details = result

        cls.log_level = details.get('log_level', 'DEBUG')

        if details.get('image_path'):
            cls.image_path = details.get('image_path')
        else:
            from tdb.cardbot import app
            parent_path = Path(os.path.abspath(app.__file__)).parents[2]
            cls.image_path = f'{parent_path}/images/'

        os.makedirs(cls.image_path, exist_ok=True)
