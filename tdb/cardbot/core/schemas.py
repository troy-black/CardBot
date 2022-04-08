import enum
from typing import Optional

from tdb.cardbot import schemas


class CardTypes(enum.Enum):
    CARD_FACE = 'card_face'
    CARD = 'card'


class CardRarity(enum.Enum):
    BONUS = 'bonus'
    COMMON = 'common'
    MYTHIC = 'mythic'
    RARE = 'rare'
    SPECIAL = 'special'
    UNCOMMON = 'uncommon'


class CardBorderColor(enum.Enum):
    BLACK = 'black'
    BORDERLESS = 'borderless'
    GOLD = 'gold'
    SILVER = 'silver'
    WHITE = 'white'


class Card(schemas.BaseSchema):
    id: str
    object_type: CardTypes
    name: str
    set: str
    set_name: Optional[str]
    lang: str
    type_line: Optional[str]
    oracle_text: Optional[str]
    rarity: Optional[CardRarity]
    collector_number: Optional[str]

    printed_name: Optional[str]
    printed_type_line: Optional[str]
    printed_text: Optional[str]
    flavor_text: Optional[str]

    mana_cost: Optional[str]
    colors: Optional[list]
    color_identity: Optional[list]
    cmc: Optional[float]
    power: Optional[str]
    toughness: Optional[str]
    loyalty: Optional[str]
    border_color: Optional[CardBorderColor]
    frame: Optional[str]
    frame_effects: Optional[list]
    layout: Optional[str]
    keywords: Optional[list]
    artist: Optional[str]
    variation: Optional[bool]
    variation_of: Optional[str]
    flavor_name: Optional[str]
    foil: Optional[bool]
    nonfoil: Optional[bool]
    oversized: Optional[bool]
    promo: Optional[bool]
    full_art: Optional[bool]
    textless: Optional[bool]
    watermark: Optional[str]
    security_stamp: Optional[str]
    reserved: Optional[bool]

    scryfall_id: str
    mtgjson_uuid: Optional[str]
    oracle_id: Optional[str]
    cardmarket_id: Optional[str]
    tcgplayer_id: Optional[str]

    image_local: Optional[str]
    image_url: Optional[str]

    phash_32: Optional[str]
    phash_48: Optional[str]
    phash_64: Optional[str]

    class Config:
        orm_mode = True


class CardMeta(schemas.BaseSchema):
    id: str
    legalities: Optional[dict]
    edhrec_rank: Optional[int]
    prices: Optional[dict]

    class Config:
        orm_mode = True


class CardHistoricPricing(schemas.BaseSchema):
    id: str
    cardkingdom_buylist_foil: Optional[dict]
    cardkingdom_buylist_normal: Optional[dict]
    cardkingdom_retail_foil: Optional[dict]
    cardkingdom_retail_normal: Optional[dict]
    cardmarket_retail_foil: Optional[dict]
    cardmarket_retail_normal: Optional[dict]
    tcgplayer_buylist_foil: Optional[dict]
    tcgplayer_buylist_normal: Optional[dict]
    tcgplayer_retail_foil: Optional[dict]
    tcgplayer_retail_normal: Optional[dict]

    class Config:
        orm_mode = True
