from fastapi import APIRouter

from tdb.cardbot.node import gpio
from tdb.cardbot.routes import BaseRoutes


class Routes(BaseRoutes):
    router = APIRouter()

    @staticmethod
    @router.get('/z/{steps}')
    def move_head(steps: int):
        gpio.Gpio.z_stepper.step(steps)
        return True

    @staticmethod
    @router.get('/x/{steps}')
    def move_x(steps: int):
        gpio.Gpio.x_stepper.step(steps)
        return True

    @staticmethod
    @router.get('/input/{steps}')
    def move_new(steps: int):
        gpio.Gpio.input_stepper.step(steps)
        return True

    @staticmethod
    @router.get('/output/{steps}')
    def move_sorted(steps: int):
        gpio.Gpio.output_stepper.step(steps)
        return True
