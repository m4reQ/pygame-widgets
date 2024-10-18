import enum


class ExpandPolicy(enum.IntEnum):
    EXPAND = enum.auto()
    MIN = enum.auto()

class OverflowBehavior(enum.IntEnum):
    OVERFLOW = enum.auto()
    UNDERFLOW = enum.auto()

class VAlignment(enum.IntEnum):
    TOP = enum.auto()
    BOTTOM = enum.auto()
    CENTER = enum.auto()

class HAlignment(enum.IntEnum):
    LEFT = enum.auto()
    RIGHT = enum.auto()
    CENTER = enum.auto()

class MainAxisSize(enum.IntEnum):
    MIN = enum.auto()
    EVEN = enum.auto()

class ImageFilter(enum.IntEnum):
    NEAREST = enum.auto()
    LINEAR = enum.auto()

class ImageSource(enum.IntEnum):
    MEMORY = enum.auto()
    FILE = enum.auto()
    URL = enum.auto()

class TextAlign(enum.IntEnum):
    '''
    An enum used in `Text.__init__(align)`.
    Represents alignment of text in a widget.
    '''

    LEFT = enum.auto()
    RIGHT = enum.auto()
    CENTER = enum.auto()

class TextFit(enum.IntEnum):
    '''
    An enum used in `Text.__init__(fit)`.
    Determines if text widget should attempt to fit the
    text if it doesn't fit inside.
    '''
    FIT = enum.auto()
    CROP = enum.auto()

class Direction(enum.IntEnum):
    LEFT = enum.auto()
    RIGHT = enum.auto()
    UP = enum.auto()
    DOWN = enum.auto()

class Side(enum.IntEnum):
    LEFT = enum.auto()
    RIGHT = enum.auto()
    TOP = enum.auto()
    BOTTOM = enum.auto()
