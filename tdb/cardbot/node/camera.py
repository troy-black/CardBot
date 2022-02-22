import io
import logging
import time


import picamera


class PiCameraDriver:
    camera: picamera.PiCamera
    stream: io.BytesIO

    last_image_bytes: bytes

    @classmethod
    def activate(cls):
        logging.debug(f'Initializing PiCamera')

        cls.camera = picamera.PiCamera(sensor_mode=1)
        cls.camera.resolution = (4056, 3040)
        cls.camera.framerate_range = (0.005, 30)

        cls.camera.exposure_mode = 'auto'

        cls.camera.iso = 100
        cls.camera.brightness = 50
        cls.camera.shutter_speed = 0

        cls.stream = io.BytesIO()

        logging.debug(f'Initialized PiCamera: wait 2')
        time.sleep(2)

    @classmethod
    def deactivate(cls):
        if cls.camera and not cls.camera.closed:
            cls.camera.close()

    @classmethod
    def capture(cls):
        logging.debug(f'Capturing Image')
        cls.camera.capture(cls.stream, 'jpeg', use_video_port=False)

        # return current frame
        cls.stream.seek(0)
        cls.last_image_bytes = cls.stream.read()

        # reset stream for next frame
        cls.stream.seek(0)
        cls.stream.truncate()
        logging.debug(f'Captured Image')

        return cls.last_image_bytes
