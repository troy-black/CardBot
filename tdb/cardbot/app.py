import logging

from fastapi import FastAPI

from tdb.cardbot import routes

logging.debug('Starting Application')

app = FastAPI()

app.include_router(routes.router)
