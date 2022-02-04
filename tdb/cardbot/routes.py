from http import HTTPStatus
from pathlib import Path

from fastapi import APIRouter
from starlette.background import BackgroundTasks
from starlette.templating import Jinja2Templates

from tdb.cardbot import futures
from tdb.cardbot.api import Api

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(str(Path(__file__).parent), 'templates')))


@router.get('/database/update', status_code=HTTPStatus.ACCEPTED)
async def scryfall_process(background_tasks: BackgroundTasks):
    return futures.JobPool.run(background_tasks, Api.update_data)
