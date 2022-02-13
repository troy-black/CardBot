from tdb.cardbot.config import BaseConfig
from tdb.cardbot.node import config
from tdb.cardbot.main import BaseMain


class Main(BaseMain):
    config: BaseConfig = config.Config


if __name__ == '__main__':
    Main.launch()
