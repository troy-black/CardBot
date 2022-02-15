import threading
import time
from enum import Enum

import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)


class SwitchType(Enum):
    IR = 0
    SWITCH = 1


class Stepper:
    def __init__(self, step_pin: int, direction_pin: int, home_pin: int, limit_pin: int = None,
                 *, home_type: SwitchType = SwitchType.SWITCH, limit_type: SwitchType = SwitchType.SWITCH):

        self.step_pin: int = self._setup_output(step_pin)
        self.direction_pin: int = self._setup_output(direction_pin)

        self.home_pin: int = self._setup_input(home_pin)
        self.home_type: SwitchType = home_type

        self.limit_pin: int = self._setup_input(limit_pin)
        self.limit_type: SwitchType = limit_type

    @staticmethod
    def _setup_output(pin: int, initial: int = 0):
        GPIO.setup(pin, GPIO.OUT, initial=initial)
        return pin

    @staticmethod
    def _setup_input(pin: int):
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        return pin


class Gpio:
    z_stepper = Stepper(10, 9, 7, 12)
    x_stepper = Stepper(11, 5, 8)

    input_stepper = Stepper(19, 26, 18, 23, limit_type=SwitchType.IR)
    output_stepper = Stepper(6, 13, 24, 25, limit_type=SwitchType.IR)

    # cls.vacuum_pump = cls._setup_output(16)

    @classmethod
    def step(cls, stepper: Stepper, direction: str, steps: int):
        GPIO.output(stepper.direction_pin, direction)
        for _ in range(steps):
            GPIO.output(stepper.step_pin, 1)
            time.sleep(0.0025)
            GPIO.output(stepper.step_pin, 0)
            time.sleep(0.0025)

            if direction in ('left', 'up'):
                limit_pin = stepper.limit_pin
                limit_type = stepper.limit_type
            else:
                limit_pin = stepper.home_pin
                limit_type = stepper.home_type

            if limit_pin and GPIO.input(limit_pin) == limit_type:
                break

    @classmethod
    def _run(cls):
        # cls.setup()

        # TODO - Add safe shutdown call
        while True:
            for stepper in (cls.z_stepper, cls.x_stepper, cls.input_stepper, cls.output_stepper):
                print(stepper)
                print('home', GPIO.input(stepper.home_pin))

                if stepper.limit_pin:
                    print('limit', GPIO.input(stepper.limit_pin))

                time.sleep(0.25)

    @classmethod
    def run(cls):
        thread = threading.Thread(target=cls._run)
        thread.start()
