import datetime
from typing import Optional

from pydantic import BaseModel


class BaseSchema(BaseModel):
    def print(self):
        return self.__class__.__name__


class NewCard(BaseSchema):
    id: str
    object_type: str

    name: Optional[str]
    type_line: Optional[str]

    lang: Optional[str]

    oracle_text: Optional[str]

    flavor_text: Optional[str]

    printed_name: Optional[str]
    printed_type_line: Optional[str]
    printed_text: Optional[str]

    set: Optional[str]
    set_name: Optional[str]

    rarity: Optional[str]
    collector_number: Optional[str]

    colors: Optional[list]
    color_identity: Optional[list]
    color_indicator: Optional[list]

    mana_cost: Optional[str]
    cmc: Optional[str]

    power: Optional[str]
    toughness: Optional[str]
    loyalty: Optional[str]

    border_color: Optional[str]
    frame: Optional[str]
    frame_effects: Optional[list]
    layout: Optional[str]

    keywords: Optional[list]

    image_url: Optional[str]
    image_local: Optional[str]
    artist: Optional[str]

    scryfall_id: Optional[str]
    mtgjson_uuid: Optional[str]
    oracle_id: Optional[str]
    mtgo_id: Optional[str]
    cardmarket_id: Optional[str]
    tcgplayer_id: Optional[str]

    legalities: Optional[dict]

    reserved: Optional[bool]
    reprint: Optional[bool]

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

    prices: Optional[dict]

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

    def print(self):
        return f'[{self.set}] {self.printed_name or self.name} [{self.collector_number}]'


# class CardMarket(Enum):
#     # TODO - ENUMS
#     pass


class CardFull(NewCard):
    phash_32: Optional[str]

    def price_schema(self):
        data = {}
        return self.__class__(**data)


class JobDetails(BaseSchema):
    job_id: Optional[int]
    job_type: str
    start_time: datetime.datetime = datetime.datetime.now()
    end_time: Optional[datetime.datetime]
    status: str = 'running'
    results: Optional[dict]

    class Config:
        orm_mode = True
