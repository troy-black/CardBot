import logging
import threading
import time
from enum import Enum
from typing import Optional, List

from tdb.cardbot.futures import Thread, ThreadPool

try:
    import RPi.GPIO as GPIO
    MAX_STEPS = 50_000
except ImportError:
    import Mock.GPIO as GPIO
    MAX_STEPS = 500


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
    current_step: int

    def __init__(self, name: str, step_pin: int, direction_pin: int, home_pin: int, limit_pin: Optional[int],
                 *, home_direction: int,
                 home_type: SwitchType = SwitchType.SWITCH,
                 limit_type: SwitchType = SwitchType.SWITCH,
                 default_count: int = None):

        self.name = name

        self.step_pin: int = self.setup_output(step_pin)
        self.direction_pin: int = self.setup_output(direction_pin)

        self.home_pin: int = self.setup_input(home_pin)
        self.home_type: SwitchType = home_type

        if limit_pin:
            self.limit_pin: int = self.setup_input(limit_pin)
        else:
            self.limit_pin = None

        self.limit_type: SwitchType = limit_type

        self.home_direction: int = home_direction

        if not limit_pin and not default_count:
            raise NotImplementedError('This is not a valid setup')

        # TODO - Find a better max count
        self.default_steps = -(default_count or MAX_STEPS)

        self.current_step = 0

        self.lock = threading.Lock()

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

    def step(self, steps: int = None, home: bool = False) -> int:
        if not self.lock.locked():

            with self.lock:
                if not steps or home:
                    steps = self.default_steps

                logging.debug(f'{self.name} Stepping...')

                GPIO.output(self.direction_pin, self.direction(steps > 0))

                count_by = int(steps / abs(steps))

                for current_step in range(0, steps, count_by):
                    if self.check_limit(steps > 0):
                        logging.debug(f'{self.name} Limit Hit @ {self.current_step}')
                        # self.lock.release()
                        return current_step

                    GPIO.output(self.step_pin, 1)
                    time.sleep(0.0025)
                    GPIO.output(self.step_pin, 0)
                    time.sleep(0.0025)

                    self.current_step += count_by

                if home:
                    self.current_step = 0

                logging.debug(f'{self.name} Stepping complete @ {self.current_step}')

                # self.lock.release()

        return self.current_step


class VacuumPump(Motor):
    def __init__(self, pump_pin: int):
        self.pump_pin: int = self.setup_output(pump_pin)

    def change(self, on: bool) -> bool:
        GPIO.output(self.pump_pin, int(on))
        return on


class Gpio:
    z_stepper = Stepper('z_stepper', 10, 9, 7, 12, home_direction=1)
    x_stepper = Stepper('x_stepper', 11, 5, 8, None, home_direction=0, default_count=460)
    x_stepper.lock = z_stepper.lock

    input_stepper = Stepper('input_stepper', 19, 26, 18, 23, home_direction=0, limit_type=SwitchType.IR)
    output_stepper = Stepper('output_stepper', 6, 13, 24, 25, home_direction=0, limit_type=SwitchType.IR)

    vacuum_pump = VacuumPump(16)

    @classmethod
    def setup(cls):
        # Reset vacuum
        cls.vacuum_pump.change(False)

        # # Home all steppers
        # cls.z_stepper.step(home=True)
        # cls.input_stepper.step(home=True)
        # cls.output_stepper.step(home=True)
        #
        # cls.x_stepper.step(home=True)
        #
        # # Move card stacks to ready pos at the top
        # cls.input_stepper.step(steps=-cls.input_stepper.default_steps)
        # cls.output_stepper.step(steps=-cls.output_stepper.default_steps)

        threads: List[Thread] = [
            # Home all steppers
            Thread(cls.z_stepper.step, home=True),
            Thread(cls.input_stepper.step, home=True),
            Thread(cls.output_stepper.step, home=True),

            Thread(cls.x_stepper.step, home=True),

            # Move card stacks to ready pos at the top
            Thread(cls.input_stepper.step, steps=-cls.input_stepper.default_steps),
            Thread(cls.output_stepper.step, steps=-cls.output_stepper.default_steps)
        ]

        results = ThreadPool.run(threads, thread_prefix='gpio')

        return results
        # return True

    @classmethod
    def loop(cls):
        cls.x_stepper.step(-cls.x_stepper.default_steps)

        cls.z_stepper.step(-cls.z_stepper.default_steps)

        cls.vacuum_pump.change(True)
        time.sleep(.5)

        cls.z_stepper.step(home=True)

        threads: List[Thread] = [
            Thread(cls.x_stepper.step, home=True),
            Thread(cls.input_stepper.step, steps=-cls.input_stepper.default_steps),
            Thread(cls.output_stepper.step, steps=-500),
        ]
        ThreadPool.run(threads, thread_prefix='gpio')

        cls.z_stepper.step(-cls.z_stepper.default_steps)

        cls.vacuum_pump.change(False)
        time.sleep(.5)

        threads: List[Thread] = [
            Thread(cls.z_stepper.step, home=True),
            Thread(cls.output_stepper.step, steps=-cls.input_stepper.default_steps),
        ]
        ThreadPool.run(threads, thread_prefix='gpio')
