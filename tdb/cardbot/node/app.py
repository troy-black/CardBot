from fastapi import APIRouter

from tdb.cardbot import app
from tdb.cardbot.crud import job
from tdb.cardbot.node import camera, config, database, gpio, routes


class App(app.BaseApp):
    router: APIRouter = routes.Routes.router
    config = config.NodeConfig

    @classmethod
    def _setup(cls):
        # Bind DB Model Object to each DB Table
        database.Database.base.metadata.create_all(bind=database.Database.engine())

        # Clear temp table(s)
        with database.Database.db_contextmanager() as db:
            job.Job.truncate(db)


@App.app.on_event("startup")
def startup_event():
    gpio.Gpio.setup()

    camera.PiCameraDriver.activate()
    camera.PiCameraDriver.camera.start_preview()


@App.app.on_event("shutdown")
def shutdown_event():
    camera.PiCameraDriver.deactivate()


if __name__ == '__main__':
    App.launch()
