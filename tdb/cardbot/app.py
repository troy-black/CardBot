import logging

from fastapi import FastAPI

from tdb.cardbot import routes
from tdb.cardbot.database import Database

logging.debug('Starting Application')

# Bind DB Model Object to each DB Table
Database.base.metadata.create_all(bind=Database.engine())

# Load FastApi Service
app = FastAPI()

# Load API routes
app.include_router(routes.router)
