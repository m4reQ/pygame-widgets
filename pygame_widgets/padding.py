import typing as t
import uuid

import pygame as pg

from .widget import SingleChildContainerWidget, Widget


class PaddingValue:
    @t.overload
    def __init__(self, x: int) -> None: ...

    @t.overload
    def __init__(self, horizontal: int, vertical: int) -> None: ...

    @t.overload
    def __init__(self, left: int, right: int, top: int, bottom: int) -> None: ...

    def __init__(self, *args) -> None:
        if len(args) == 1:
            self.left = args[0]
            self.right = args[0]
            self.top = args[0]
            self.bottom = args[0]
        elif len(args) == 2:
            self.left = self.right = args[0]
            self.top = self.bottom = args[1]
        elif len(args) == 4:
            self.left = args[0]
            self.right = args[1]
            self.top = args[2]
            self.bottom = args[3]
        else:
            raise ValueError('Invalid padding arguments.')

    @property
    def axis_x(self) -> int:
        return self.left + self.right

    @property
    def axis_y(self) -> int:
        return self.top + self.bottom

class Padding(SingleChildContainerWidget):
    def __init__(self,
                 child: Widget,
                 padding: PaddingValue,
                 *,
                 _id: uuid.UUID | None = None,
                 rect: pg.Rect | None = None) -> None:
        super().__init__(child, _id, rect)

        self._padding = padding

    def calculate_size(self, max_width: int, max_height: int) -> tuple[int, int]:
        super().calculate_size(max_width, max_height)

        child_width = max_width - self._padding.axis_x
        child_height = max_height - self._padding.axis_y

        self.child.calculate_size(child_width, child_height)

        self.rect.width = max_width
        self.rect.height = max_height

        return (max_width, max_height)

    def set_placement(self, x: int, y: int) -> None:
        super().set_placement(x, y)

        self.child.set_placement(x + self._padding.left, y + self._padding.top)

