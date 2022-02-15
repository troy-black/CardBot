from fastapi import APIRouter

from tdb.cardbot.app import BaseApp
from tdb.cardbot.node import config
from tdb.cardbot.node import gpio
from tdb.cardbot.node import routes


class App(BaseApp):
    router: APIRouter = routes.Routes.router
    config = config.Config


@App.app.on_event("startup")
def startup_event():
    gpio.Gpio.run()


if __name__ == '__main__':
    App.launch()
