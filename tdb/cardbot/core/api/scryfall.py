import logging
from typing import List

from tdb.cardbot.core import utils

BULK_DATA = 'https://api.scryfall.com/bulk-data'


class Scryfall:
    @classmethod
    def download_data(cls) -> List[dict]:
        """
        Download 'default_cards' from api.scryfall.com. Used to match scryfall images with mtgjson data

        :return: dict containing Scryfall Api Image URL info keyed by scryfallId and cardName
        """
        logging.debug(f'Downloading Scryfall Bulk Data')

        # Extract download_uri from bulk data for default_cards
        download_uri = next(
            data['download_uri']
            for data in utils.download_file(BULK_DATA)['data']
            if data['type'] == 'all_cards'
        )

        default_cards = utils.download_file(download_uri)

        return default_cards
