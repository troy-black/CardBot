from pathlib import Path

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from starlette.templating import Jinja2Templates

from tdb.cardbot import models
from tdb.cardbot.api.mtgjson import MTGJson
from tdb.cardbot.api.scryfall import Scryfall
from tdb.cardbot.database import SessionLocal, engine

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(str(Path(__file__).parent), 'templates')))

models.Base.metadata.create_all(bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get('/mtgjson/process')
def mtgjson_process(db: Session = Depends(get_db)):
    MTGJson.process_all_printings(db)
    Scryfall.process_bulk_data(db)
