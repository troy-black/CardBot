from fastapi import APIRouter

from tdb.cardbot.node import gpio
from tdb.cardbot.routes import BaseRoutes


class Routes(BaseRoutes):
    router = APIRouter()

    @staticmethod
    @router.get('/z/{steps}')
    def move_head(steps: int):
        return gpio.Gpio.z_stepper.step(steps)

    @staticmethod
    @router.get('/x/{steps}')
    def move_x(steps: int):
        return gpio.Gpio.x_stepper.step(steps)

    @staticmethod
    @router.get('/input/{steps}')
    def move_new(steps: int):
        return gpio.Gpio.input_stepper.step(steps)

    @staticmethod
    @router.get('/output/{steps}')
    def move_sorted(steps: int):
        return gpio.Gpio.output_stepper.step(steps)

    @staticmethod
    @router.get('/vacuum/{on}')
    def vacuum(on: bool):
        return gpio.Gpio.vacuum_pump.change(on)

    @staticmethod
    @router.get('/setup')
    async def setup():
        return gpio.Gpio.setup()

    @staticmethod
    @router.get('/loop')
    async def loop():
        return gpio.Gpio.loop()
