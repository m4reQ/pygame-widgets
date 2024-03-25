import uuid

import pygame as pg

from pygame_widgets.widget import ContainerWidget, Widget


class Stack(ContainerWidget):
    def __init__(self,
                 children: list[Widget],
                 _id: uuid.UUID | None = None,
                 rect: pg.Rect | None = None) -> None:
        super().__init__(children, _id, rect)

    def calculate_size(self, max_width: int, max_height: int) -> tuple[int, int]:
        super().calculate_size(max_width, max_height)

        _max_width = 0
        _max_height = 0

        for child in self._children:
            child_width, child_height = child.calculate_size(max_width, max_height)
            _max_width = max(_max_width, child_width)
            _max_height = max(_max_height, child_height)

        for child in self._children:
            child.calculate_size(_max_width, _max_height)

        self.rect.width = _max_width
        self.rect.height = _max_height

        return self.rect.size

    def set_placement(self, x: int, y: int) -> None:
        super().set_placement(x, y)

        for child in self._children:
            child.set_placement(x, y)
