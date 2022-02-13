from fastapi import APIRouter

from tdb.cardbot.app import BaseApp
from tdb.cardbot.node import gpio
from tdb.cardbot.node import routes


class App(BaseApp):
    router: APIRouter = routes.router


@App.app().on_event("startup")
def startup_event():
    gpio.Gpio.run()
