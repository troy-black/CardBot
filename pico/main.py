import time

import machine
import rp2


class PIODriver:
    _driver_ids = set()

    def __init__(self, driver_id: int, frequency: int, direction_pin: int, driver_pin: int, limit_pin: int):
        if driver_id < 0 or driver_id > 7:
            assert False, 'Driver id 0-7 only'

        if driver_id in PIODriver._driver_ids:
            assert False, 'Driver id already assigned'

        PIODriver._driver_ids.add(driver_id)

        self.id: int = driver_id
        self.location: int = 0
        self.direction_pin = machine.Pin(direction_pin, machine.Pin.OUT)

        self.state_machine = rp2.StateMachine(
            driver_id,
            PIODriver.stepper_assembly_pio_program,
            freq=frequency,
            set_base=machine.Pin(driver_pin, machine.Pin.OUT),
            jmp_pin=machine.Pin(limit_pin, machine.Pin.IN, machine.Pin.PULL_DOWN)
        )

        self._driver_pin_number: int = driver_pin
        self._direction_pin_number: int = direction_pin
        self._limit_pin_number: int = limit_pin
        self._frequency: int = frequency

    def logger(self, statement: str):
        print('{}[{}]|{}'.format(self.__class__.__name__, self.id, statement))

    def step(self, direction: int, steps: int, delay: int):
        self.logger('Stepping: {} x {}'.format(direction, steps))

        self.direction_pin.value(direction)

        self.state_machine.irq(self.stepper_assembly_pio_irq)
        self.state_machine.active(1)

        self.state_machine.put(steps)
        self.state_machine.put(delay)

        time.sleep(5)

        self.state_machine.active(0)

        # pin = machine.Pin(self._driver_pin_number, machine.Pin.OUT)
        # pin.value(0)

        self.logger('All done Stepping: {} x {}'.format(direction, steps))

    def stepper_assembly_pio_irq(self, state_machine):
        rx_fifo = state_machine.get()
        self.location = rx_fifo

    @staticmethod
    @rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
    def stepper_assembly_pio_program():
        pull()                                  # read from the TX FIFO into osr        (MAX CYCLE COUNT)
        mov(y, osr)                             # copy osr data into y                  (y = REMAINING CYCLE)
        pull()                                  # read from the TX FIFO into osr        (DELAY CYCLE COUNT)

        label('step')                           # goto                                  (LABEL: step)

        mov(x, osr)                             # copy osr data into x                  (x = REMAINING DELAY CYCLES)

        set(pins, 1)                            # pulse high                            (SQUARE WAVE FUNCTION)

        label('delay')                          # goto                                  (LABEL: delay)

        set(pins, 0)                            # pulse low                             (SQUARE WAVE FUNCTION)

        jmp(pin, 'trigger')                     # if (jmp_pin)                          (GOTO: trigger)
        jmp(x_dec, 'delay')                     # if (x-- > 1) (decrease after eval)    (GOTO: delay)

        jmp(y_dec, 'step')                      # if (y-- > 1) (decrease after eval)    (GOTO: step)

        label('trigger')                        # goto                                  (LABEL: trigger)

        mov(isr, y)                             # copy y (REMAINING CYCLE) into isr
        push()                                  # print isr to RX FIFO

        irq(rel(0))                             # irq MicroPython callback function


class DcMotor:
    def __init__(self,
                 clockwise_pin_number: int,
                 clockwise_freq: int,
                 clockwise_duty: int,
                 counterclockwise_pin_number: int,
                 counterclockwise_freq: int,
                 counterclockwise_duty: int,
                 ):
        self._clockwise_pin_number = clockwise_pin_number
        self._counterclockwise_pin_number = counterclockwise_pin_number

        self.clockwise_pin = machine.PWM(machine.Pin(clockwise_pin_number))
        self.clockwise_pin.freq(clockwise_freq)
        self.clockwise_pin.duty_u16(clockwise_duty)

        self.counterclockwise_pin = machine.PWM(machine.Pin(counterclockwise_pin_number))
        self.counterclockwise_pin.freq(counterclockwise_freq)
        self.counterclockwise_pin.duty_u16(counterclockwise_duty)

    def step(self, direction: int, start_duty_cycle: int, max_duty_cycle: int, increment: int, steps: int):
        print('Stepping :{} x {}'.format(direction, steps))

        if direction == 0:
            self.counterclockwise_pin.duty_u16(0)
            motor = self.clockwise_pin
        else:
            self.clockwise_pin.duty_u16(0)
            motor = self.counterclockwise_pin

        count = 0

        def duty_cycle(_count, _dc):
            print('Step {} of {} [{}]'.format(_count, steps, _dc))
            motor.duty_u16(_dc)
            time.sleep(0.05)
            return _count + 1

        for dc in range(start_duty_cycle, max_duty_cycle, increment):
            count = duty_cycle(count, dc)

        for _ in range(count, steps):
            count = duty_cycle(count, max_duty_cycle)

        motor.duty_u16(0)


# class StepperMotor:
#     def __init__(self, stepper_pin_number: int, direction_pin_number: int):
#         self._stepper_pin_number = stepper_pin_number
#         self._direction_pin_number = direction_pin_number
#
#         self._direction_pin = machine.Pin(direction_pin_number, machine.Pin.OUT)
#         self._direction_pin.value(0)
#
#         self._stepper_pin = machine.Pin(stepper_pin_number, machine.Pin.OUT)
#         self._stepper_pin.value(0)
#
#     def step(self, direction: int, steps: int):
#         print('Stepping :{} x {}'.format(direction, steps))
#         self._direction_pin.value(direction)
#
#         for s in range(steps):
#             print('Step {} of {}'.format(s, steps))
#             self._stepper_pin.value(1)
#             time.sleep(0.001)
#             self._stepper_pin.value(0)
#             time.sleep(0.001)


# class UARTProcess:
#     COMMAND_PARSE = b'\n'
#
#     buffer: bytes
#
#     def __init__(self):
#         self.uart0 = machine.UART(0, baudrate=9600, tx=machine.Pin(0), rx=machine.Pin(1))
#
#         self.reset()
#
#     def decode_buffer(self, decode: str = 'utf-8', split: str = ','):
#         print('Buffer: {0}'.format(self.buffer))
#
#     def reset(self):
#         self.buffer = b''
#
#     def send(self):
#         #  TODO - Add Logic here to send some response back to the client
#         # response = '{0}\n'.format(self.alt_az.drive_data)
#         self.uart0.write('response')
#
#     def tick(self):
#         if self.uart0.any():
#             last_bytes: bytes = self.uart0.read()
#
#             while self.COMMAND_PARSE in last_bytes:
#                 index = last_bytes.index(self.COMMAND_PARSE)
#                 self.buffer += last_bytes[:index]
#                 last_bytes = last_bytes[index + 1:]
#
#             self.buffer += last_bytes
#             self.decode_buffer()
#
#             self.reset()


def main():

    stepper1 = PIODriver(0, 10000, 12, 11, 10)
    stepper1.step(1, 1000, 5)
    stepper1.step(0, 1000, 5)
    stepper1.step(1, 1000, 5)

    # dc1 = PIODriver(1, 10000, 19, 20, 10)
    # dc1.step(1, 2000, 2)
    # dc1.step(0, 2000, 2)

    dc_motor = DcMotor(
        19, 100, 0,
        20, 100, 0
    )
    dc_motor.step(1, 0, 65535, 3500, 50)
    dc_motor.step(0, 0, 65535, 3500, 50)
    dc_motor.step(1, 0, 65535, 3500, 50)

    # uart = UARTProcess()
    #
    # while True:
    #     uart.tick()
    #     time.sleep(0.1)  # TODO - Can this be changed???


if __name__ == '__main__':
    main()
