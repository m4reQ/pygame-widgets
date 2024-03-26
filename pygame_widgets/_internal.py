import math

from pygame_widgets.enums import OverflowBehavior


def set_overflow_behavior(behavior: OverflowBehavior) -> None:
    global _overflow_behavior
    _overflow_behavior = behavior

def round(x: int | float) -> int:
    if _overflow_behavior == OverflowBehavior.OVERFLOW:
        return math.ceil(x)

    return math.floor(x)

def divide_with_overflow(x: int | float, y: int | float) -> int:
    return round(x / y)

_overflow_behavior = OverflowBehavior.UNDERFLOW
