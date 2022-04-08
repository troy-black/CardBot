from sqlalchemy import Column, Integer, String, JSON, Boolean

from tdb.cardbot.node import database


class CardScan(database.Database.base):
    __tablename__ = 'scans'

    scan_id = Column(Integer, primary_key=True, index=True)

    stack_name = Column(String, index=True)
    stack_index = Column(Integer, index=True)

    card_id = Column(String, index=True)

    closest_matches = Column(JSON)

    language = Column(String)

    foil = Column(Boolean)
    proxy = Column(Boolean)
    altered = Column(Boolean)
