import math
import uuid

import pygame as pg

from .widget import ContainerWidget, Widget


class Row(ContainerWidget):
    def __init__(self,
                 children: list[Widget],
                 *,
                 spacing: int = 0,
                 _id: uuid.UUID | None = None,
                 rect: pg.Rect | None = None) -> None:
        super().__init__(children, _id, rect)

        self._spacing = spacing
        self._max_child_width = 0

    def calculate_size(self, max_width: int, max_height: int) -> tuple[int, int]:
        super().calculate_size(max_width, max_height)

        height = 0

        avail_width = max_width - self._spacing * (len(self._children) - 1)
        self._max_child_width = math.floor(avail_width / len(self._children))

        x_offset = 0
        for child in self._children:
            _, child_height = child.calculate_size(self._max_child_width, max_height)

            height = max(height, child_height)
            x_offset += self._max_child_width + self._spacing

        self.rect.width = x_offset
        self.rect.height = height

        return (x_offset, height)

    def set_placement(self, x: int, y: int) -> None:
        super().set_placement(x, y)

        offset_x = 0
        for child in self._children:
            child.set_placement(x + offset_x, y)
            offset_x += self._max_child_width + self._spacing

    def recalculate(self) -> None:
        super().recalculate()

        self.rect.width = sum(x.get_size()[0] for x in self._children) + (len(self._children) - 1) * self._spacing
        self.rect.height = max(x.get_size()[1] for x in self._children)
