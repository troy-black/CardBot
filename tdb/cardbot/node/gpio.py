import threading
import time

import RPi.GPIO as GPIO


class Gpio:
    # Outputs
    z_step: int
    z_dir: int

    x_step: int
    x_dir: int

    sort_lift_step: int
    sort_lift_dir: int

    new_lift_step: int
    new_lift_dir: int

    vacuum_pump: int

    # Inputs
    new_lift_up_ir: int
    new_lift_down_switch: int

    sort_lift_up_ir: int
    sort_lift_down_switch: int

    z_up_switch: int
    z_down_switch: int

    x_home_switch: int

    @classmethod
    def setup(cls):
        GPIO.setmode(GPIO.BCM)
    
        # Outputs
        cls.z_step = cls._setup_output(10)
        cls.z_dir = cls._setup_output(9)
    
        cls.x_step = cls._setup_output(11)
        cls.x_dir = cls._setup_output(5)
    
        cls.sort_lift_step = cls._setup_output(6)
        cls.sort_lift_dir = cls._setup_output(13)
    
        cls.new_lift_step = cls._setup_output(19)
        cls.new_lift_dir = cls._setup_output(26)
    
        cls.vacuum_pump = cls._setup_output(16)
    
        # Inputs
        cls.new_lift_down_switch = cls._setup_input(18)
        cls.new_lift_up_ir = cls._setup_input(23)

        cls.sort_lift_down_switch = cls._setup_input(24)
        cls.sort_lift_up_ir = cls._setup_input(25)
    
        cls.z_up_switch = cls._setup_input(7)
        cls.z_down_switch = cls._setup_input(12)

        cls.x_home_switch = cls._setup_input(8)

    @classmethod
    def _setup_output(cls, pin: int, initial: int = 0):
        GPIO.setup(pin, GPIO.OUT, initial=initial)
        return pin

    @classmethod
    def _setup_input(cls, pin: int):
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        return pin

    @classmethod
    def _run(cls):
        cls.setup()

        # TODO - Add safe shutdown call
        while True:
            print('new_lift_down_switch', GPIO.input(cls.new_lift_down_switch))
            print('new_lift_up_ir', GPIO.input(cls.new_lift_up_ir))

            print('sort_lift_down_switch', GPIO.input(cls.sort_lift_down_switch))
            print('sort_lift_up_ir', GPIO.input(cls.sort_lift_up_ir))

            print('x_home_switch', GPIO.input(cls.x_home_switch))

            print('z_up_switch', GPIO.input(cls.z_up_switch))
            print('z_down_switch', GPIO.input(cls.z_down_switch))

            time.sleep(0.25)

    @classmethod
    def move_head(cls, direction: str, steps: int):
        if direction == 'up':
            limit_pin = cls.z_up_switch
            direction = 1
        else:
            limit_pin = cls.z_down_switch
            direction = 0

        cls._step(cls.z_dir, cls.z_step, limit_pin, direction, steps, 1)

    @classmethod
    def move_x(cls, direction: str, steps: int):
        if direction == 'left':
            limit_pin = None
            direction = 1
        else:
            limit_pin = cls.x_home_switch
            direction = 0

        cls._step(cls.x_dir, cls.x_step, limit_pin, direction, steps, 1)

    @classmethod
    def move_new_lift(cls, direction: str, steps: int):
        if direction == 'up':
            limit_pin = cls.new_lift_up_ir
            limit_type = 0
            direction = 1
        else:
            limit_pin = cls.new_lift_down_switch
            limit_type = 1
            direction = 0

        cls._step(cls.new_lift_dir, cls.new_lift_step, limit_pin, direction, steps, limit_type)

    @classmethod
    def move_sorted_lift(cls, direction: str, steps: int):
        if direction == 'up':
            limit_pin = cls.sort_lift_up_ir
            limit_type = 0
            direction = 1
        else:
            limit_pin = cls.sort_lift_down_switch
            limit_type = 1
            direction = 0

        cls._step(cls.sort_lift_dir, cls.sort_lift_step, limit_pin, direction, steps, limit_type)

    @classmethod
    def _step(cls, direction_pin: int, step_pin: int, limit_pin: int, direction: int, steps: int, limit_type: int):
        GPIO.output(direction_pin, direction)
        for _ in range(steps):
            GPIO.output(step_pin, 1)
            time.sleep(0.0025)
            GPIO.output(step_pin, 0)
            time.sleep(0.0025)

            if limit_pin and GPIO.input(limit_pin) == limit_type:
                break

    @classmethod
    def run(cls):
        thread = threading.Thread(target=cls._run)
        thread.start()
