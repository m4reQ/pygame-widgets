import uuid

import pygame as pg

from pygame_widgets.widget import Widget


class Rect(Widget):
    def __init__(self,
                 color: pg.Color,
                 *,
                 rounding: int = 0,
                 width: int = 0,
                 _id: uuid.UUID | None = None,
                 rect: pg.Rect | None = None) -> None:
        super().__init__(_id, rect)

        self._color = color
        self._rounding = rounding
        self._width = width

    def redraw(self) -> None:
        flags = 0
        if self._rounding != 0 or self._color.a != 255:
            flags = pg.SRCALPHA

        self.image = pg.Surface(self.rect.size, flags)

        if self._rounding != 0:
            pg.draw.rect(
                self.image,
                self._color,
                self.image.get_rect(),
                width=self._width,
                border_radius=self._rounding)
        else:
            self.image.fill(self._color)

    def calculate_size(self, max_width: int, max_height: int ) -> tuple[int, int]:
        super().calculate_size(max_width, max_height)

        self.rect.width = max_width
        self.rect.height = max_height

        return (max_width, max_height)

    def recalculate(self) -> None:
        super().recalculate()

        if self._constraints != (-1, -1):
            self.rect.size = self._constraints

    @property
    def color(self) -> pg.Color:
        return self._color

    @color.setter
    def color(self, value: pg.Color) -> None:
        self._color = value
        self._needs_redraw = True

    @property
    def rounding(self) -> int:
        return self._rounding

    @rounding.setter
    def rounding(self, value: int) -> None:
        self._rounding = value
        self._needs_redraw = True

    @property
    def width(self) -> int:
        return self._width

    @width.setter
    def width(self, value: int) -> None:
        self._width = value
        self._needs_redraw = True
