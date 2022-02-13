import logging
from enum import Enum

from tdb.cardbot.core import utils

MTGJSON_API_URL = 'https://mtgjson.com/api/v5/'


class Filenames(Enum):
    ALL_PRINTINGS = 'AllPrintings.json.xz'
    ALL_PRICES = 'AllPrices.json.xz'


class MTGJson:
    @classmethod
    def download_data(cls, filename: Filenames) -> dict:
        """
        Download file from mtgjson.com

        :return: dict containing complete card data by card set
        """
        data = utils.download_file(f'{MTGJSON_API_URL}{filename.value}')

        meta: dict = data['meta']
        logging.debug(f'MTGJson Meta {filename.value}: {meta}')

        return data['data']

    @classmethod
    def download_prices(cls) -> dict:
        """
        Download Paper format Card pricing from

        :return: dict containing complete paper format pricing
        """
        all_prices = cls.download_data(Filenames.ALL_PRICES)

        card_format: dict
        for uuid, card_format in all_prices.items():
            # Keep only paper pricing
            for key in list(card_format.keys()):
                if key != 'paper':
                    card_format.pop(key)

        return all_prices
