import datetime
from typing import List, Optional

import pydantic


class BaseSchema(pydantic.BaseModel):
    def print(self):
        return self.__class__.__name__


class HashDetails(BaseSchema):
    card_id: str
    name: str
    lang: str
    card_set: str
    card_diff: float
    max_diff: float
    avg_diff: float
    phash: str
    # crop_coords: List[Tuple[int, int]]


class ProcessedImage(pydantic.BaseModel):
    closest_matches: List[str]
    process_image: bytes
    matched_image: bytes


class JobDetails(BaseSchema):
    job_id: Optional[int]
    job_type: str
    start_time: datetime.datetime = datetime.datetime.now()
    end_time: Optional[datetime.datetime]
    status: str = "running"
    results: Optional[dict]

    class Config:
        orm_mode = True
