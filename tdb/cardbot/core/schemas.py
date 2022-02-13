import datetime
from datetime import date
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel


class BaseSchema(BaseModel):
    def print(self):
        return self.__class__.__name__


class SetFull(BaseSchema):
    code: str
    name: str
    keyruneCode: Optional[str]
    releaseDate: Optional[date]

    parentCode: Optional[str]
    totalSetSize: Optional[int]

    class Config:
        orm_mode = True

    def print(self):
        return f'[{self.code}] {self.name}'


class NewCard(BaseSchema):
    uuid: str
    name: str
    asciiName: Optional[str]
    setCode: str
    number: str
    colorIdentity: Optional[List[str]]
    colors: Optional[List[str]]
    manaCost: Optional[str]
    rarity: Optional[str]
    artist: Optional[str]

    imageUrl: Optional[str]
    imageLocal: Optional[str]

    faceName: Optional[str]

    subtypes: Optional[List[str]]
    supertypes: Optional[List[str]]
    text: Optional[str]
    type: Optional[str]
    types: Optional[List[str]]

    flavorName: Optional[str]
    flavorText: Optional[str]
    keywords: Optional[List[str]]
    loyalty: Optional[str]
    manaValue: Optional[int]
    power: Optional[str]
    toughness: Optional[str]

    scryfallId: Optional[str]

    availability: Optional[List[str]]
    hasAlternativeDeckLimit: Optional[bool]
    # edhrecRank: Optional[int]

    borderColor: Optional[str]
    finishes: Optional[List[str]]
    frameEffects: Optional[List[str]]
    frameVersion: Optional[str]
    layout: Optional[str]
    securityStamp: Optional[str]
    watermark: Optional[str]

    hasFoil: Optional[bool]
    hasNonFoil: Optional[bool]
    isAlternative: Optional[bool]
    isFullArt: Optional[bool]
    isOnlineOnly: Optional[bool]
    isOversized: Optional[bool]
    isPromo: Optional[bool]
    isRebalanced: Optional[bool]
    isReprint: Optional[bool]
    isReserved: Optional[bool]

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

    # cardSet: Optional[SetFull]

    class Config:
        orm_mode = True

    def print(self):
        return f'[{self.setCode}] {self.faceName or self.asciiName or self.name} [{self.number}]'


class CardMarket(Enum):
    # TODO - ENUMS
    pass


class CardFull(NewCard):
    searchName: Optional[str]
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


class LogDetails(BaseSchema):
    time: datetime.datetime
    level: str
    thread_name: str
    location: str
    message: str

    class Config:
        orm_mode = True