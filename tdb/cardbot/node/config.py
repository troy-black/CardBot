import os
import pathlib

from tdb.cardbot import config


class NodeConfig(config.BaseConfig):
    app: str = 'tdb.cardbot.node.app:App'
    image_path: str = '/home/pi/CardBot/images/'

    core_url = 'http://black:8000'

    @classmethod
    def _load(cls, details: dict):
        if details.get('image_path'):
            cls.image_path = details.get('image_path')
        else:
            # Set default to 2 parents from the base app ('../../images/')
            from tdb.cardbot import app
            parent_path = pathlib.Path(os.path.abspath(app.__file__)).parents[2]
            cls.image_path = f'{parent_path}/images/'

        # Create path if it doesn't exist
        os.makedirs(cls.image_path, exist_ok=True)
