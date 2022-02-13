import os
from pathlib import Path

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Date, Computed, DateTime
from sqlalchemy.dialects.postgresql import JSON

from tdb.cardbot.core import config
from tdb.cardbot.core.database import Database
from tdb.cardbot.core.image import Image
from tdb.cardbot.core.utils import download_file


class Card(Database.base):
    __tablename__ = 'cards'

    uuid = Column(String(36), primary_key=True, index=True)

    name = Column(String, nullable=False, index=True)
    asciiName = Column(String, index=True)
    faceName = Column(String)

    searchName = Column(String, Computed(
        '''
            CASE 
                WHEN "faceName" IS NOT NULL THEN "faceName" 
                WHEN "asciiName" IS NOT NULL THEN "asciiName" 
                ELSE name 
            END
        '''
    ))

    setCode = Column(String, ForeignKey('sets.code'), nullable=False, index=True)
    number = Column(String, nullable=False)

    colorIdentity = Column(JSON)
    colors = Column(JSON)
    manaCost = Column(String)
    rarity = Column(String)
    artist = Column(String)

    imageUrl = Column(String)
    imageLocal = Column(String)

    subtypes = Column(JSON)
    supertypes = Column(JSON)
    text = Column(String)
    type = Column(String)
    types = Column(JSON)

    flavorName = Column(String)
    flavorText = Column(String)
    keywords = Column(JSON)
    loyalty = Column(String)
    manaValue = Column(Float)
    power = Column(String)
    toughness = Column(String)

    scryfallId = Column(String)

    availability = Column(JSON)
    hasAlternativeDeckLimit = Column(Boolean)
    # edhrecRank = Column(Integer)

    borderColor = Column(String)
    finishes = Column(JSON)
    frameEffects = Column(JSON)
    frameVersion = Column(String)
    layout = Column(String)
    securityStamp = Column(String)
    watermark = Column(String)

    hasFoil = Column(Boolean)
    hasNonFoil = Column(Boolean)
    isAlternative = Column(Boolean)
    isFullArt = Column(Boolean)
    isOnlineOnly = Column(Boolean)
    isOversized = Column(Boolean)
    isPromo = Column(Boolean)
    isRebalanced = Column(Boolean)
    isReprint = Column(Boolean)
    isReserved = Column(Boolean)

    # cardSet = relationship('Set')

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
        if not self.imageUrl:
            return

        filename = str(Path(config.Config.image_path, self.imageLocal))

        new_hash = False
        if not os.path.exists(filename):
            download_file(url=self.imageUrl, filename=filename)
            new_hash = True

        if new_hash or not self.phash_32:
            phash = Image(Path(config.Config.image_path, self.setCode, f'{self.scryfallId}.png'))
            self.phash_32 = str(phash.image_hash())


class Set(Database.base):
    __tablename__ = 'sets'

    code = Column(String(8), primary_key=True, index=True)
    name = Column(String)
    keyruneCode = Column(String)
    parentCode = Column(String)
    releaseDate = Column(Date)
    totalSetSize = Column(Integer)


class Job(Database.base):
    __tablename__ = 'jobs'

    job_id = Column(Integer, primary_key=True)
    job_type = Column(String, index=True)
    start_time = Column(DateTime, index=True)
    end_time = Column(DateTime)
    status = Column(String)
    results = Column(JSON)


class Log(Database.base):
    __tablename__ = 'logs'

    log_id = Column(Integer, primary_key=True)
    time = Column(DateTime, index=True)
    level = Column(String)
    thread_name = Column(String)
    location = Column(String)
    message = Column(String)
