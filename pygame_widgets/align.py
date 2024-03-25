import enum
import uuid

import pygame as pg

from . import _internal
from .widget import SingleChildContainerWidget, Widget


class VAlignment(enum.Enum):
    TOP = enum.auto()
    BOTTOM = enum.auto()
    CENTER = enum.auto()

class HAlignment(enum.Enum):
    LEFT = enum.auto()
    RIGHT = enum.auto()
    CENTER = enum.auto()

class Align(SingleChildContainerWidget):
    def __init__(self,
                 child: Widget,
                 *,
                 vertical: VAlignment = VAlignment.CENTER,
                 horizontal: HAlignment = HAlignment.CENTER,
                 _id: uuid.UUID | None = None,
                 rect: pg.Rect | None = None) -> None:
        super().__init__(child, _id, rect)

        self._vertical = vertical
        self._horizontal = horizontal

        self._available_width = 0
        self._available_height = 0

    def calculate_size(self, max_width: int, max_height: int) -> tuple[int, int]:
        super().calculate_size(max_width, max_height)

        self.rect.width, self.rect.height = self.child.calculate_size(max_width, max_height)
        self._available_width = max_width
        self._available_height = max_height

        return self.rect.size

    def set_placement(self, x: int, y: int) -> None:
        new_x = x
        if self._horizontal == HAlignment.CENTER:
            new_x += _internal.divide_with_overflow(abs(self._available_width - self.rect.width), 2)
        elif self._horizontal == HAlignment.RIGHT:
            new_x += self._available_width - self.rect.width

        new_y = y
        if self._vertical == VAlignment.CENTER:
            new_y += _internal.divide_with_overflow(abs(self._available_height - self.rect.height), 2)
        elif self._vertical == VAlignment.BOTTOM:
            new_y += self._available_height - self.rect.height

        self.child.set_placement(new_x, new_y)
        super().set_placement(new_x, new_y)

class Center(Align):
    def __init__(self,
                 child: Widget,
                 _id: uuid.UUID | None = None,
                 rect: pg.Rect | None = None) -> None:
        super().__init__(
            child,
            vertical=VAlignment.CENTER,
            horizontal=HAlignment.CENTER,
            _id=_id,
            rect=rect)
