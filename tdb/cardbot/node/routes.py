from typing import Union

from fastapi import APIRouter
from starlette.responses import Response

from tdb.cardbot.node import camera
from tdb.cardbot.node import gpio
from tdb.cardbot.routes import BaseRoutes


class Routes(BaseRoutes):
    router = APIRouter()

    @staticmethod
    @router.get('/z/{steps}', response_model=int)
    def move_head(steps: int):
        return gpio.Gpio.z_stepper.step(steps)

    @staticmethod
    @router.get('/x/{steps}', response_model=int)
    def move_x(steps: int):
        return gpio.Gpio.x_stepper.step(steps)

    @staticmethod
    @router.get('/input/{steps}', response_model=int)
    def move_new(steps: int):
        return gpio.Gpio.input_stepper.step(steps)

    @staticmethod
    @router.get('/output/{steps}', response_model=int)
    def move_sorted(steps: int):
        return gpio.Gpio.output_stepper.step(steps)

    @staticmethod
    @router.get('/vacuum/{on}', response_model=bool)
    def vacuum(on: bool):
        return gpio.Gpio.vacuum_pump.change(on)

    # @staticmethod
    # @router.get('/setup')
    # async def setup():
    #     return gpio.Gpio.setup()

    @staticmethod
    @router.get('/loop')
    async def loop():
        return gpio.Gpio.loop()

    # TODO - Testing....
    @staticmethod
    @router.get('/preview/{on}', response_model=bool)
    def preview(on: bool):
        if on:
            camera.PiCameraDriver.camera.start_preview()
        else:
            camera.PiCameraDriver.camera.stop_preview()

        return on

    @staticmethod
    @router.get('/prop/{prop}/{val}', response_model=bool)
    def prop_change(prop: str, val: Union[int, str]):
        if hasattr(camera.PiCameraDriver.camera, prop):
            setattr(camera.PiCameraDriver.camera, prop, val)
            return True

        return False

    @staticmethod
    @router.get('/capture')
    def capture():
        camera.PiCameraDriver.capture()
        return Response(camera.PiCameraDriver.last_image_bytes, media_type='image/jpeg')
