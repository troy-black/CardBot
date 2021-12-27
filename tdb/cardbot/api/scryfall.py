import logging
import os
from pathlib import Path

from sqlalchemy.orm import Session

from cardbot import utils
from cardbot.crud.card import Card
from tdb.cardbot import config
from tdb.cardbot.utils import download_file

BULK_DATA = 'https://api.scryfall.com/bulk-data'


class Scryfall:
    @classmethod
    def download_json(cls, url: str) -> dict:
        return utils.download_file(url)

    @classmethod
    def process_bulk_data(cls, db: Session):
        download_uri = next(
            data['download_uri']
            for data in cls.download_json(BULK_DATA)['data']
            if data['type'] == 'default_cards'
        )

        updates = 0
        for data in cls.download_json(download_uri):
            scryfall_id = data['id']

            if data.get('card_faces'):
                if data.get('card_faces')[0].get('image_uris'):
                    card_faces = {
                        card_face['name']: card_face.get('image_uris', {}).get('png')
                        for card_face in data.get('card_faces')
                    }
                else:
                    card_faces = {
                        card_face['name']: data.get('image_uris', {}).get('png')
                        for card_face in data.get('card_faces')
                    }
            else:
                card_faces = {
                    card_face['name']: card_face.get('image_uris', {}).get('png')
                    for card_face in [data]
                }

            for card_name, png_url in card_faces.items():
                if card_name and png_url:
                    card = Card.read_one_by_scryfall_and_name(db, scryfall_id, card_name)
                    if card:
                        filename = str(Path(config.Config.image_path, card.setCode, f'{card.scryfallId}.png'))

                        if card.imageUrl != png_url:
                            if card.imageUrl:
                                os.remove(card.imageLocal)

                            if not os.path.exists(filename):
                                download_file(
                                    url=png_url,
                                    filename=filename
                                )

                            card.imageUrl = png_url
                            card.imageLocal = filename
                            updates += 1

            logging.debug(f'Syncing Image [{updates}]: {card_name}')

            if updates % 100 == 0:
                db.commit()

        db.commit()
