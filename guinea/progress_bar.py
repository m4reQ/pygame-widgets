import uuid

import pygame as pg

from guinea import _internal
# from pygame_widgets._internal import (TargetFill, apply_target_fill_to_surface,
#                                       get_surface_flags_for_target_fill)
from guinea.widget import Widget

DEFAULT_BG = pg.Color(0, 0, 0, 255)
DEFAULT_FG = pg.Color(0, 255, 0, 255)

class ProgressBar(Widget):
    def __init__(self,
                 start_value: float,
                 max_value: float | None,
                 *,
                 fg: _internal.TargetFill = DEFAULT_FG,
                 bg: _internal.TargetFill = DEFAULT_BG,
                 rounding: int = 0,
                 _id: uuid.UUID | None = None,
                 rect: pg.Rect | None = None) -> None:
        super().__init__(_id, rect)

        assert max_value is not None, "Indefinite progress bar is not implemented yet"

        self.image = pg.Surface((0, 0))

        self._max_value = max_value
        self._value = start_value
        self._fg = fg
        self._bg = bg
        self._rounding = rounding

    def calculate_size(self, max_width: int, max_height: int) -> tuple[int, int]:
        self.rect.width = max_width
        self.rect.height = max_height

        return (max_width, max_height)

    def set_placement(self, x: int, y: int) -> None:
        self.rect.x = x
        self.rect.y = y

    def redraw(self) -> None:
        surf_flags = 0
        if self._rounding != 0:
            surf_flags |= pg.SRCALPHA

        img = pg.Surface(
            self.rect.size,
            surf_flags)

        if isinstance(self._bg, pg.Color):
            if self._rounding != 0:
                fill_rect = pg.Rect(
                    0,
                    0,
                    img.get_width(),
                    img.get_height())
                pg.draw.rect(img, self._bg, fill_rect, border_radius=self._rounding)
            else:
                img.fill(self._bg)

        fill_rect = pg.Rect(
            0,
            0,
            _internal.round(self.rect.width * (self._value / self._max_value)),
            self.rect.height)
        if isinstance(self._fg, pg.Color):
            if self._rounding != 0:
                pg.draw.rect(
                    img,
                    self._fg,
                    fill_rect,
                    border_top_left_radius=self._rounding,
                    border_bottom_left_radius=self._rounding)
            else:
                img.fill(self._fg, fill_rect)

        # img.fill(
        #     pg.Color(0, 0, 0, 255),
        #     pg.Rect(
        #         0,
        #         0,
        #         _internal.round(self.rect.width * self._value / self._max_value),
        #         self.rect.height))
        # _internal.apply_target_fill_to_surface(img, self._bg, False)
        # apply_target_fill_to_surface()

        # bar_img = pg.Surface(
        # 	(, self.rect.height),
          # 	get_surface_flags_for_target_fill(self._fg))
        # apply_target_fill_to_surface(bar_img, )

        self.image = img

    def increment(self, value: float) -> None:
        self._value = max(self._value + value, self._max_value)
        self._needs_redraw = True

    @property
    def value(self) -> float:
        return self._value

    @property
    def max_value(self) -> float:
        return self._max_value
