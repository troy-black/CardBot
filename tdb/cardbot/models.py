from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Date
from sqlalchemy.dialects.postgresql import JSON

# from sqlalchemy.orm import relationship

from tdb.cardbot.database import Base


class Card(Base):
    __tablename__ = 'cards'

    uuid = Column(String(36), primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    asciiName = Column(String, index=True)
    setCode = Column(String, ForeignKey('sets.code'), nullable=False, index=True)
    number = Column(String, nullable=False)
    colorIdentity = Column(JSON)

    colors = Column(JSON)
    manaCost = Column(String)
    rarity = Column(String)
    artist = Column(String)

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

    # multiverseId = Column(String)
    # scryfallId = Column(String)

    identifiers = Column(JSON)

    availability = Column(JSON)
    hasAlternativeDeckLimit = Column(Boolean)
    edhrecRank = Column(Integer)

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


class Set(Base):
    __tablename__ = 'sets'

    code = Column(String(8), primary_key=True, index=True)
    name = Column(String)
    keyruneCode = Column(String)
    parentCode = Column(String)
    releaseDate = Column(Date)
    totalSetSize = Column(Integer)
