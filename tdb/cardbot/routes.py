import datetime
from http import HTTPStatus
from pathlib import Path
from typing import List, Union

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException
from starlette.templating import Jinja2Templates

from tdb.cardbot.api import Api
from tdb.cardbot.crud.job import Job
from tdb.cardbot.crud.log import Log
from tdb.cardbot.database import Database
from tdb.cardbot.schemas import LogDetails, JobDetails

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(str(Path(__file__).parent), 'templates')))


@router.get('/database/update', status_code=HTTPStatus.ACCEPTED, response_model=JobDetails)
async def database_update() -> JobDetails:
    """
    Update Database from Scryfall and MTGJson Api

    :return: JobDetails
    """
    return await Api.run()


@router.get('/logs', response_model=List[LogDetails])
async def get_logs(db: Session = Depends(Database.get_db)) -> List[LogDetails]:
    """
    Stream the most recent Application Logs

    :param db: SqlAlchemy DB Session
    :return: List[LogDetails]
    """
    return Log.read_logs(db)


@router.get('/jobs/{key}', response_model=JobDetails)
async def get_job(key: Union[int, str], db: Session = Depends(Database.get_db)) -> JobDetails:
    """
    Get JobDetails

    :param key: Identifying key (Job Number or Job Type)
    :param db: SqlAlchemy DB Session
    :return: JobDetails
    """
    return Job.read_one(db, key)


@router.get('/jobs/{key}/stop', response_model=JobDetails)
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
