import os
from pathlib import Path

from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import JSON

from tdb.cardbot.core import config
from tdb.cardbot.core.database import Database
from tdb.cardbot.core.image import Image
from tdb.cardbot.core.utils import download_file


class Card(Database.base):
    __tablename__ = 'cards'

    id = Column(String, primary_key=True, index=True)
    object_type = Column(String, index=True)

    name = Column(String, index=True)
    type_line = Column(String)

    lang = Column(String, index=True)

    oracle_text = Column(String)

    flavor_text = Column(String)

    printed_name = Column(String)
    printed_type_line = Column(String)
    printed_text = Column(String)

    set = Column(String, index=True)
    set_name = Column(String)

    rarity = Column(String)
    collector_number = Column(String)

    colors = Column(JSON)
    color_identity = Column(JSON)
    color_indicator = Column(JSON)

    mana_cost = Column(String)
    cmc = Column(String)

    power = Column(String)
    toughness = Column(String)
    loyalty = Column(String)

    border_color = Column(String, index=True)
    frame = Column(String)
    frame_effects = Column(JSON)
    layout = Column(String)

    keywords = Column(JSON)

    image_url = Column(String)
    image_local = Column(String)
    artist = Column(String)

    scryfall_id = Column(String, index=True)
    mtgjson_uuid = Column(String, index=True)
    oracle_id = Column(String)
    mtgo_id = Column(String)
    cardmarket_id = Column(String)
    tcgplayer_id = Column(String)

    legalities = Column(JSON)

    reserved = Column(Boolean)
    reprint = Column(Boolean)

    variation = Column(Boolean)
    variation_of = Column(String)
    flavor_name = Column(String)

    foil = Column(Boolean)
    nonfoil = Column(Boolean)

    oversized = Column(Boolean)

    promo = Column(Boolean)
    full_art = Column(Boolean)
    textless = Column(Boolean)

    watermark = Column(String)
    security_stamp = Column(String)

    prices = Column(JSON)

    phash_32 = Column(String)

    cardkingdom_buylist_foil = Column(JSON)
    cardkingdom_buylist_normal = Column(JSON)
    cardkingdom_retail_foil = Column(JSON)
    cardkingdom_retail_normal = Column(JSON)

    cardmarket_retail_foil = Column(JSON)
    cardmarket_retail_normal = Column(JSON)

    tcgplayer_buylist_foil = Column(JSON)
    tcgplayer_buylist_normal = Column(JSON)
    tcgplayer_retail_foil = Column(JSON)
    tcgplayer_retail_normal = Column(JSON)

    def download_image(self):
        """
        Download image from Scryfall Api
        """
        if not self.image_url:
            return

        filepath = Path(config.Config.image_path, self.image_local)
        filename = str(filepath)

        new_hash = False
        if not os.path.exists(filename):
            download_file(url=self.image_url, filename=filename)
            new_hash = True

        if new_hash or not self.phash_32:
            image = Image(filepath)
            phash = image.image_hash()
            if phash:
                self.phash_32 = str(phash)


class Job(Database.base):
    __tablename__ = 'jobs'

    job_id = Column(Integer, primary_key=True)
    job_type = Column(String, index=True)
    start_time = Column(DateTime, index=True)
    end_time = Column(DateTime)
    status = Column(String)
    results = Column(JSON)
