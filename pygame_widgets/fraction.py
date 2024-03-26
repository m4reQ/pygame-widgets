import uuid

import pygame as pg

from pygame_widgets import _internal
from pygame_widgets.widget import SingleChildContainerWidget, Widget


class Fraction(SingleChildContainerWidget):
    def __init__(self,
                 child: Widget,
                 factor: tuple[float, float],
                 _id: uuid.UUID | None = None,
                 rect: pg.Rect | None = None) -> None:
        super().__init__(child, _id, rect)

        self._factor = factor

    def calculate_size(self, max_width: int, max_height: int) -> tuple[int, int]:
        super().calculate_size(max_width, max_height)

        self.rect.width, self.rect.height = self.child.calculate_size(
            _internal.round(max_width * self._factor[0]),
            _internal.round(max_height * self._factor[1]))

        return self.rect.size

    def set_placement(self, x: int, y: int) -> None:
        super().set_placement(x, y)

        self.child.set_placement(x, y)
