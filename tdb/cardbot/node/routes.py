from fastapi import APIRouter

from tdb.cardbot.node import gpio

router = APIRouter()


@router.get('/test')
def test():
    return True


# TODO - The number of steps should be the same everytime
@router.get('/head/{direction}/{steps}')
def move_head(direction, steps: int):
    gpio.Gpio.move_head(direction, steps)
    return True


# TODO - The number of steps should be the same everytime
@router.get('/x/{direction}/{steps}')
def move_x(direction, steps: int):
    gpio.Gpio.move_x(direction, steps)
    return True


# TODO - The number of steps should be the same everytime
@router.get('/new/{direction}/{steps}')
def move_x(direction, steps: int):
    gpio.Gpio.move_new_lift(direction, steps)
    return True


# TODO - The number of steps should be the same everytime
@router.get('/sorted/{direction}/{steps}')
def move_x(direction, steps: int):
    gpio.Gpio.move_sorted_lift(direction, steps)
    return True

