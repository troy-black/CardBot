from typing import List, Optional

from tdb.cardbot import schemas


class CardScanDetails(schemas.BaseSchema):
    scan_id: Optional[int]

    stack_name: str
    stack_index: int

    card_id: str

    closest_matches: List[str]

    language: str = 'en'

    foil: bool = False
    proxy: bool = False
    altered: bool = False

    class Config:
        orm_mode = True
