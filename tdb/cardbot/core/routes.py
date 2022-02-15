import datetime
from http import HTTPStatus
from typing import Union

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException

from tdb.cardbot.core.api import Api
from tdb.cardbot.core.crud.job import Job
from tdb.cardbot.core.database import Database
from tdb.cardbot.core.schemas import JobDetails
from tdb.cardbot.routes import BaseRoutes


class Routes(BaseRoutes):
    router = APIRouter()

    @staticmethod
    @router.get('/database/update', status_code=HTTPStatus.ACCEPTED, response_model=JobDetails)
    async def database_update() -> JobDetails:
        """
        Update Database from Scryfall and MTGJson Api

        :return: JobDetails
        """
        return await Api.run()

    @staticmethod
    @router.get('/job/{key}', response_model=JobDetails)
    async def get_job(key: Union[int, str], db: Session = Depends(Database.get_db)) -> JobDetails:
        """
        Get JobDetails

        :param key: Identifying key (Job Number or Job Type)
        :param db: SqlAlchemy DB Session
        :return: JobDetails
        """
        job = Job.read_one(db, key)

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        return job

    @staticmethod
    @router.get('/job/{key}/stop', response_model=JobDetails)
    async def stop_job(key: Union[int, str], db: Session = Depends(Database.get_db)) -> JobDetails:
        """
        Send a Stop request to running Background Job

        :param key: Identifying key (Job Number or Job Type)
        :param db: SqlAlchemy DB Session
        :return: JobDetails
        """
        job = Job.read_one(db, key)

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        job.status = 'canceled'
        job.results = {'canceled': datetime.datetime.now().isoformat()}

        db.commit()
        db.refresh(job)

        return job
