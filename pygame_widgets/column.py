import math
import uuid

import pygame as pg

from pygame_widgets.widget import ContainerWidget, Widget


class Column(ContainerWidget):
    def __init__(self,
                 children: list[Widget],
                 *,
                 spacing: int = 0,
                 _id: uuid.UUID | None = None,
                 rect: pg.Rect | None = None) -> None:
        super().__init__(children, _id, rect)

        self._spacing = spacing
        self._max_child_height = 0

    def calculate_size(self, max_width: int, max_height: int) -> tuple[int, int]:
        super().calculate_size(max_width, max_height)

        width = 0

        avail_height = max_height - self._spacing * (len(self._children) - 1)
        self._max_child_height = math.floor(avail_height / len(self._children))

        y_offset = 0
        for child in self._children:
            child_width, _ = child.calculate_size(max_width, self._max_child_height)

            width = max(width, child_width)
            y_offset += self._max_child_height + self._spacing

        self.rect.width = width
        self.rect.height = y_offset

        return (width, y_offset)

    def set_placement(self, x: int, y: int) -> None:
        super().set_placement(x, y)

        offset_y = 0
        for child in self._children:
            child.set_placement(x, y + offset_y)
            offset_y += self._max_child_height + self._spacing

    def recalculate(self) -> None:
        super().recalculate()

        self.rect.width = max(x.get_size()[0] for x in self._children)
        self.rect.height = sum(x.get_size()[1] for x in self._children) + (len(self._children) - 1) * self._spacing
