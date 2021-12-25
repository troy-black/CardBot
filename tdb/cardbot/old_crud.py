import logging
from typing import List

from sqlalchemy.orm import Session

from tdb.cardbot import models, schemas


def create_card(db: Session, card_full: schemas.CardFull, *, commit: bool = True) -> models.Card:
    card = models.Card(**card_full.dict())
    db.add(card)

    if commit:
        db.commit()
        db.refresh(card)

    return card


def get_card(db: Session, uuid: str) -> models.Card:
    return db.query(models.Card).filter(models.Card.uuid == uuid).first()


def get_cards(db: Session, skip: int = 0, limit: int = 100) -> List[models.Card]:
    return db.query(models.Card).offset(skip).limit(limit).all()


def get_cards_by_name(db: Session, name: str,  skip: int = 0, limit: int = 100) -> List[models.Card]:
    return db.query(models.Card).filter(
        models.Card.name == name or models.Card.asciiName == name
    ).offset(skip).limit(limit).all()


def upsert_card(db: Session, card_full: schemas.CardFull) -> models.Card:
    changes = {}
    record: models.Card = get_card(db, card_full.uuid)

    if record:
        for key, val in card_full.dict().items():
            if hasattr(record, key) and getattr(record, key, 0) != val:
                setattr(record, key, val)
                changes[key] = val

        if changes:
            logging.debug(f'Updating Card: {changes}')

    else:
        record: models.Card = models.Card(**card_full.dict())
        db.add(record)
        changes = True
        logging.debug(f'Adding Card: {card_full.dict()}')

    if changes:
        db.commit()
        db.refresh(record)

    return record


def create_set(db: Session, set_full: schemas.SetFull) -> models.Set:
    _set = models.Set(**set_full.dict())
    db.add(_set)
    db.commit()
    db.refresh(_set)
    return _set


def get_set(db: Session, code: str) -> models.Set:
    return db.query(models.Set).filter(models.Set.code == code).first()


def get_sets(db: Session, skip: int = 0, limit: int = 100) -> List[models.Set]:
    return db.query(models.Set).offset(skip).limit(limit).all()


def upsert_set(db: Session, set_full: schemas.SetFull) -> models.Set:
    changes = {}
    record: models.Set = get_set(db, set_full.code)

    if record:
        for key, val in set_full.dict().items():
            if hasattr(record, key) and getattr(record, key, 0) != val:
                setattr(record, key, val)
                changes[key] = val

        if changes:
            logging.debug(f'Updating Set: {changes}')

    else:
        record = models.Set(**set_full.dict())
        db.add(record)
        changes = True
        logging.debug(f'Adding Set: {set_full.dict()}')

    if changes:
        db.commit()
        db.refresh(record)

    return record
