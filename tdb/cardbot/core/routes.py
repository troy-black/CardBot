import base64
import datetime
from http import HTTPStatus
from pathlib import Path
from typing import Union, Optional

from PIL import Image as PillowImage
from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException

from tdb.cardbot import image
from tdb.cardbot import routes, schemas as base_schemas
from tdb.cardbot.core import api
from tdb.cardbot.core import database
from tdb.cardbot.core import hashing, models, config
from tdb.cardbot.core.crud import card
from tdb.cardbot.crud import job


class Routes(routes.BaseRoutes):
    router = APIRouter()

    @staticmethod
    @router.get('/database/update', status_code=HTTPStatus.ACCEPTED, response_model=base_schemas.JobDetails)
    async def database_update() -> base_schemas.JobDetails:
        """
        Update Database from Scryfall and MTGJson Api

        :return: JobDetails
        """
        return await api.Api.run()

    @staticmethod
    @router.get('/job/{key}', response_model=base_schemas.JobDetails)
    async def get_job(key: Union[int, str], db: Session = Depends(database.Database.get_db)) -> base_schemas.JobDetails:
        """
        Get JobDetails

        :param key: Identifying key (Job Number or Job Type)
        :param db: SqlAlchemy DB Session
        :return: JobDetails
        """
        job_record = job.Job.read_one(db, key)

        if not job_record:
            raise HTTPException(status_code=404, detail="Job not found")

        return job_record

    @staticmethod
    @router.get('/job/{key}/stop', response_model=base_schemas.JobDetails)
    async def stop_job(key: Union[int, str], db: Session = Depends(database.Database.get_db)) -> base_schemas.JobDetails:
        """
        Send a Stop request to running Background Job

        :param key: Identifying key (Job Number or Job Type)
        :param db: SqlAlchemy DB Session
        :return: JobDetails
        """
        job_record = job.Job.read_one(db, key)

        if not job_record:
            raise HTTPException(status_code=404, detail="Job not found")

        job_record.status = 'canceled'
        job_record.results = {'canceled': datetime.datetime.now().isoformat()}

        db.commit()
        db.refresh(job_record)

        return job_record

    @staticmethod
    @router.post("/process/image", response_model=base_schemas.ProcessedImage)
    async def process_image(file: UploadFile, card_id: Optional[str] = None,
                            db: Session = Depends(database.Database.get_db)) -> base_schemas.ProcessedImage:
        last_upload = hashing.HashImage(file.file, hash_size=config.CoreConfig.phash_size)

        matches = hashing.HashTable.get_closest_matches(last_upload.image_hash.hash)

        card_record: models.Card = card.Card.read_one(db, matches[0])

        if card_id and card_id != card_record.id:
            print('Not a perfect match')

        filepath = Path(config.CoreConfig.image_path, card_record.image_local)

        last_match = image.Image(filepath)

        last_modified = last_match.modified_image

        combined_match = PillowImage.new('RGB', (last_modified.size[0] * 2, last_modified.size[1]))
        combined_match.paste(last_upload.modified_image, (0, 0))
        combined_match.paste(last_match.modified_image, (last_match.modified_image.width, 0))

        processed_image = base_schemas.ProcessedImage(
            closest_matches=matches,
            process_image=base64.b64encode(routes.BaseRoutes.pillow_image_as_bytes(last_upload.modified_image)),
            matched_image=base64.b64encode(routes.BaseRoutes.pillow_image_as_bytes(combined_match)),
        )

        return processed_image

    @staticmethod
    @router.get("/card/{card_id}/image")
    async def get_card_image(card_id: str, db: Session = Depends(database.Database.get_db)):
        card_record: models.Card = card.Card.read_one(db, card_id)

        if not card_record:
            raise HTTPException(status_code=404, detail="Card not found")

        filepath = Path(config.CoreConfig.image_path, card_record.image_local)

        img = image.Image(filepath)

        return Routes.return_pillow_image_as_png(img.modified_image)
