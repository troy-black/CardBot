from sqlalchemy import Boolean, Column, String, Integer, ForeignKey, TEXT, Enum, Float
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from tdb.cardbot.core import database
from tdb.cardbot.core import schemas

CARD_BASE_ID = 'cards.id'


class Card(database.Database.base):
    __tablename__ = 'cards'

    id = Column(String(96), primary_key=True)
    object_type = Column(
        Enum(schemas.CardTypes, values_callable=lambda x: [e.value for e in schemas.CardTypes]),
        index=True,
        nullable=False
    )
    name = Column(String(192), index=True, nullable=False)
    set = Column(String(8), index=True, nullable=False)
    set_name = Column(String(64))
    lang = Column(String(8), index=True, nullable=False)
    type_line = Column(String(96))
    oracle_text = Column(TEXT)
    rarity = Column(Enum(schemas.CardRarity, values_callable=lambda x: [e.value for e in schemas.CardRarity]))
    collector_number = Column(String(16))

    printed_name = Column(String(192))
    printed_type_line = Column(String(96))
    printed_text = Column(TEXT)
    flavor_text = Column(TEXT)

    mana_cost = Column(String(48))
    colors = Column(JSON)
    color_identity = Column(JSON)
    cmc = Column(Float)
    power = Column(String(8))
    toughness = Column(String(8))
    loyalty = Column(String(8))
    border_color = Column(Enum(schemas.CardBorderColor, values_callable=lambda x: [e.value for e in schemas.CardBorderColor]), index=True)
    frame = Column(String(8))
    frame_effects = Column(JSON)
    layout = Column(String(18))
    keywords = Column(JSON)
    artist = Column(String(64))
    variation = Column(Boolean)
    variation_of = Column(String(96))
    flavor_name = Column(String(192))
    foil = Column(Boolean)
    nonfoil = Column(Boolean)
    oversized = Column(Boolean)
    promo = Column(Boolean)
    full_art = Column(Boolean)
    textless = Column(Boolean)
    watermark = Column(String(32))
    security_stamp = Column(String(8))
    reserved = Column(Boolean)

    scryfall_id = Column(String(36), index=True)
    mtgjson_uuid = Column(String(36))
    oracle_id = Column(String(36))
    cardmarket_id = Column(String(6))
    tcgplayer_id = Column(String(6))

    image_local = Column(String(256), index=True)
    image_url = Column(String(256))

    phash_32 = Column(String(256), index=True)
    phash_48 = Column(String(576), index=True)
    phash_64 = Column(String(1024), index=True)

    meta = relationship('CardMeta', back_populates='cards', uselist=False)
    historic_pricing = relationship('CardHistoricPricing', back_populates='cards', uselist=False)


class CardMeta(database.Database.base):
    __tablename__ = 'meta'

    id = Column(String(96), ForeignKey(CARD_BASE_ID), primary_key=True)
    legalities = Column(JSON)
    edhrec_rank = Column(Integer)
    prices = Column(JSON)

    cards = relationship("Card", back_populates="meta")


class CardHistoricPricing(database.Database.base):
    __tablename__ = 'historic_pricing'

    id = Column(String(96), ForeignKey(CARD_BASE_ID), primary_key=True)
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

    cards = relationship("Card", back_populates="historic_pricing")
