from pathlib import Path
from typing import List

from fastapi import APIRouter
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.templating import Jinja2Templates

from tdb.cardbot import schemas
from tdb.cardbot import models
from tdb.cardbot.mtgjson import MTGJson
from tdb.cardbot.database import SessionLocal, engine

from tdb.cardbot import old_crud as crud


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


@router.post('/cards/', response_model=schemas.CardFull)
def create_card(card_full: schemas.CardFull, db: Session = Depends(get_db)):
    card = crud.get_card(db, uuid=card_full.uuid)
    if card:
        raise HTTPException(status_code=400, detail='uuid already registered')
    return crud.create_card(db=db, card_full=card_full)


@router.get('/cards/', response_model=List[schemas.CardFull])
def read_cards(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    cards = crud.get_cards(db, skip=skip, limit=limit)
    return cards


@router.get('/cards/{uuid}', response_model=schemas.CardFull)
def read_card(uuid: str, db: Session = Depends(get_db)):
    card = crud.get_card(db, uuid=uuid)
    if card is None:
        raise HTTPException(status_code=404, detail='Card not found')
    return card


@router.post('/sets/', response_model=schemas.SetFull)
def create_set(set_full: schemas.SetFull, db: Session = Depends(get_db)):
    return crud.create_set(db=db, set_full=set_full)


@router.get('/sets/{code}', response_model=schemas.SetFull)
def read_set(code: str, db: Session = Depends(get_db)):
    _set = crud.get_set(db, code=code)
    if _set is None:
        raise HTTPException(status_code=404, detail='Set not found')
    return _set


@router.get('/sets/', response_model=List[schemas.SetFull])
def read_sets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sets = crud.get_sets(db, skip=skip, limit=limit)
    return sets


@router.get('/mtgjson/process/ALL')
def process_file(db: Session = Depends(get_db)):
    MTGJson.download_all_printings(db)
    print()


# @router.get('/mtgjson/process/{file}')
# def process_file(file: MTGJsonFiles):
#     data = MTGJson.process(file)
#     print()
