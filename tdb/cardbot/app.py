import logging
from concurrent.futures.process import ProcessPoolExecutor

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


@app.on_event("startup")
async def startup_event():
    """
    Setup background ProcessPoolExecutor
    """
    app.state.executor = ProcessPoolExecutor()


@app.on_event("shutdown")
async def on_shutdown():
    """
    Shutdown background ProcessPoolExecutor
    """
    app.state.executor.shutdown()
