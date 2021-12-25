from datetime import date
from typing import Optional, List

from pydantic import BaseModel


class SetBase(BaseModel):
    code: str
    name: str
    keyruneCode: Optional[str]
    releaseDate: Optional[date]


class SetFull(SetBase):
    parentCode: Optional[str]
    totalSetSize: Optional[int]

    class Config:
        orm_mode = True


class CardBase(BaseModel):
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

    # cardSet: Optional[SetBase]


class CardFull(CardBase):
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

    # multiverseId: Optional[str]
    # scryfallId: Optional[str]

    identifiers: Optional[dict]

    availability: Optional[List[str]]
    hasAlternativeDeckLimit: Optional[bool]
    edhrecRank: Optional[int]

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

    # cardSet: Optional[SetFull]

    class Config:
        orm_mode = True
