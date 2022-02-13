import logging

from tdb.cardbot.core import utils

BULK_DATA = 'https://api.scryfall.com/bulk-data'


class Scryfall:
    @classmethod
    def download_data(cls) -> dict:
        """
        Download 'default_cards' from api.scryfall.com. Used to match scryfall images with mtgjson data

        :return: dict containing Scryfall Api Image URL info keyed by scryfallId and cardName
        """
        logging.debug(f'Downloading Scryfall Bulk Data')

        # Extract download_uri from bulk data for default_cards
        download_uri = next(
            data['download_uri']
            for data in utils.download_file(BULK_DATA)['data']
            if data['type'] == 'default_cards'
        )

        default_cards = utils.download_file(download_uri)

        # Build dict of IMAGE_URL keyed by (SCRYFALL_ID, CARD_NAME)
        #                Check for individual uri inside card_faces
        # example: {
        #     (SCRYFALL_ID, CARD_NAME): IMAGE_URL,
        # }
        return {
            (data['id'], card_face['name']):
                (card_face if card_face.get('image_uris') else data).get('image_uris', {}).get('png')
            for data in default_cards
            for card_face in (data.get('card_faces') or [data])
        }
