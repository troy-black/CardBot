import io
import logging
import threading
import time

import picamera


class PiCameraDriver:
    camera: picamera.PiCamera

    last_image_bytes: bytes

    threading_event: threading.Event

    @classmethod
    def activate(cls):
        logging.debug(f'Initializing PiCamera')

        cls.camera = picamera.PiCamera(sensor_mode=1)
        cls.camera.rotation = -90

        cls.camera.resolution = (1080, 1920)

        cls.camera.framerate_range = (0.005, 30)

        cls.camera.exposure_mode = 'auto'

        cls.camera.iso = 100
        cls.camera.brightness = 50
        cls.camera.shutter_speed = 0

        cls.threading_event = threading.Event()
        cls.threading_event.clear()

        logging.debug(f'Initialized PiCamera: wait 2')
        time.sleep(2)

    @classmethod
    def deactivate(cls):
        if cls.camera and not cls.camera.closed:
            cls.camera.close()

    @classmethod
    def capture(cls, filename: str = None) -> bytes:
        logging.debug(f'Capturing Image')
        cls.threading_event.set()

        stream = io.BytesIO()

        cls.camera.capture(stream, 'jpeg', use_video_port=False)

        # reset stream for next frame
        stream.seek(0)
        cls.last_image_bytes: bytes = stream.read()

        if filename:
            with open(filename, 'wb') as out_file:
                out_file.write(cls.last_image_bytes)

        cls.threading_event.clear()
        logging.debug(f'Processed Image')

        return cls.last_image_bytes
