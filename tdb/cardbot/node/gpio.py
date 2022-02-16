import threading
import time
from enum import Enum
from typing import Optional

import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)


class Direction(Enum):
    POSITIVE = 1
    NEGATIVE = 0


class SwitchType(Enum):
    IR = 0
    SWITCH = 1


class Motor:
    @staticmethod
    def setup_output(pin: int, initial: int = 0):
        GPIO.setup(pin, GPIO.OUT, initial=initial)
        return pin

    @staticmethod
    def setup_input(pin: int):
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        return pin


class Stepper(Motor):
    def __init__(self, step_pin: int, direction_pin: int, home_pin: int, limit_pin: Optional[int],
                 *, home_direction: int,
                 home_type: SwitchType = SwitchType.SWITCH,
                 limit_type: SwitchType = SwitchType.SWITCH):

        self.step_pin: int = self.setup_output(step_pin)
        self.direction_pin: int = self.setup_output(direction_pin)

        self.home_pin: int = self.setup_input(home_pin)
        self.home_type: SwitchType = home_type

        self.limit_pin: int = self.setup_input(limit_pin) if limit_pin else None
        self.limit_type: SwitchType = limit_type

        self.home_direction: int = home_direction

    def check_limit(self, positive: bool):
        if positive:
            # Move away from home position
            return self.limit_pin and GPIO.input(self.limit_pin) == self.limit_type.value

        # Move toward home position
        return GPIO.input(self.home_pin) == self.home_type.value

    def direction(self, positive: bool):
        if positive:
            # Move away from home position
            return int(not self.home_direction)

        # Move toward home position
        return self.home_direction

    def step(self, steps: int):
        GPIO.output(self.direction_pin, self.direction(steps > 0))

        for current_step in range(0, steps, int(steps / abs(steps))):
            if self.check_limit(steps > 0):
                return current_step

            GPIO.output(self.step_pin, 1)
            time.sleep(0.0025)
            GPIO.output(self.step_pin, 0)
            time.sleep(0.0025)

        return steps


class Gpio:
    z_stepper = Stepper(10, 9, 7, 12, home_direction=1)
    x_stepper = Stepper(11, 5, 8, None, home_direction=0)

    input_stepper = Stepper(19, 26, 18, 23, home_direction=0, limit_type=SwitchType.IR)
    output_stepper = Stepper(6, 13, 24, 25, home_direction=0, limit_type=SwitchType.IR)

    # cls.vacuum_pump = cls._setup_output(16)

    @classmethod
    def _run(cls):
        # TODO - Add safe shutdown call
        while True:
            steppers = {
                'z_stepper': cls.z_stepper,
                'x_stepper': cls.x_stepper,
                'input_stepper': cls.input_stepper,
                'output_stepper': cls.output_stepper
            }
            for name, stepper in steppers.items():
                print(name, 'home', GPIO.input(stepper.home_pin))

                if stepper.limit_pin:
                    print(name, 'limit', GPIO.input(stepper.limit_pin))

                time.sleep(0.25)

    @classmethod
    def run(cls):
        thread = threading.Thread(target=cls._run)
        thread.start()
