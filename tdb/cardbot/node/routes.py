from fastapi import APIRouter

from tdb.cardbot.node import gpio
from tdb.cardbot.routes import BaseRoutes


class Routes(BaseRoutes):
    router = APIRouter()

    @staticmethod
    @router.get('/head/{direction}/{steps}')
    def move_head(direction, steps: int):
        gpio.Gpio.move_head(direction, steps)
        return True

    @staticmethod
    @router.get('/x/{direction}/{steps}')
    def move_x(direction, steps: int):
        gpio.Gpio.move_x(direction, steps)
        return True

    @staticmethod
    @router.get('/new/{direction}/{steps}')
    def move_new(direction, steps: int):
        gpio.Gpio.move_new_lift(direction, steps)
        return True

    @staticmethod
    @router.get('/sorted/{direction}/{steps}')
    def move_sorted(direction, steps: int):
        gpio.Gpio.move_sorted_lift(direction, steps)
        return True
