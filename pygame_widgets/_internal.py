import enum
import math


class OverflowBehavior(enum.Enum):
    OVERFLOW = enum.auto()
    UNDERFLOW = enum.auto()

def set_overflow_behavior(behavior: OverflowBehavior) -> None:
    global _overflow_behavior
    _overflow_behavior = behavior

def divide_with_overflow(x: int | float, y: int | float) -> int:
    if _overflow_behavior == OverflowBehavior.OVERFLOW:
        return math.ceil(x / y)

    # OverflowBehavior.OVERFLOW
    return math.floor(x / y)

_overflow_behavior = OverflowBehavior.UNDERFLOW
