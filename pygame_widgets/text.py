import enum
import uuid

import pygame as pg

from pygame_widgets import _internal
from pygame_widgets.widget import Widget

_BlitTarget = tuple[pg.Surface, tuple[int, int]]

class TextAlign(enum.Enum):
    '''
    An enum used in `Text.__init__(align)`.
    Represents alignment of text in a widget.
    '''

    LEFT = enum.auto()
    RIGHT = enum.auto()
    CENTER = enum.auto()

class TextFit(enum.Enum):
    '''
    An enum used in `Text.__init__(fit)`.
    Determines if text widget should attempt to fit the
    text if it doesn't fit inside.
    '''
    FIT = enum.auto()
    CROP = enum.auto()

class Text(Widget):
    DEFAULT_FONT_FAMILY = 'Consolas'
    DEFAULT_FONT_SIZE = 24

    def __init__(self,
                 text: str,
                 *,
                 fg: pg.Color = pg.Color(0, 0, 0, 255),
                 bg: pg.Color = pg.Color(0, 0, 0, 0),
                 font: pg.font.Font | None = None,
                 antialiasing: bool = True,
                 line_spacing: int = 0,
                 tab_size: int = 4,
                 fit: TextFit = TextFit.FIT,
                 align: TextAlign = TextAlign.LEFT,
                 fill_empty_bg: bool = True,
                 _id: uuid.UUID | None = None,
                 rect: pg.Rect | None = None) -> None:
        super().__init__(_id, rect)

        self._lines = [x for x in text.replace('\t', ' ' * tab_size).split('\n') if x != '']
        self._fg = fg
        self._bg = bg
        self._align = align
        self._font = font or pg.font.SysFont(self.DEFAULT_FONT_FAMILY, self.DEFAULT_FONT_SIZE)
        self._antialiasing = antialiasing
        self._line_spacing = line_spacing
        self._tab_size = tab_size
        self._fit = fit
        self._fill_empty_bg = fill_empty_bg

        self._required_width = 0
        self._required_height = 0

        self.image = pg.Surface((0, 0))

    def _redraw_on_single_line(self, line: str) -> None:
        self.image = self._render_line(line)

    def _render_line(self, line: str) -> pg.Surface:
        if self._bg.a == 0:
            bg_color = None
        else:
            bg_color = self._bg

        result = self._font.render(
            line,
            self._antialiasing,
            self._fg,
            bg_color)

        return result

    def _fit_image(self) -> None:
        target_size = (
            min(self._required_width, self.rect.width),
            min(self._required_height, self.rect.height))

        if self._fit == TextFit.FIT:
            # TODO Implement better fit using variable font size (use calculate_size for this)
            self.image = pg.transform.smoothscale(
                self.image,
                target_size)
        else:
            self.image = self.image.subsurface((0, 0), target_size)

    def _get_x_alignment(self, avail_width: int, width: int) -> int:
        if self._align == TextAlign.RIGHT:
            return avail_width - width
        elif self._align == TextAlign.CENTER:
            return _internal.divide_with_overflow(avail_width - width, 2)

        # TextAlign.LEFT
        return 0

    def redraw(self) -> None:
        if len(self._lines) == 1:
            self._redraw_on_single_line(self._lines[0])
            return

        current_y = 0
        blit_targets: list[_BlitTarget] = []
        for line in self._lines:
            surf = self._render_line(line)
            target = (surf, (self._get_x_alignment(self._required_width, surf.get_width()), current_y))
            blit_targets.append(target)

            current_y += surf.get_height() + self._line_spacing

        flags = 0
        if self._bg.a == 0 or not self._fill_empty_bg:
            flags = pg.SRCALPHA

        self.image = pg.Surface((self._required_width, self._required_height), flags)
        if self._fill_empty_bg and self._bg.a != 0:
            self.image.fill(self._bg)

        self.image.blits(blit_targets, False)

        if self._required_width > self.rect.width or self._required_height > self.rect.height:
            self._fit_image()

    def calculate_size(self, max_width: int, max_height: int) -> tuple[int, int]:
        super().calculate_size(max_width, max_height)

        required_height = 0
        required_width = 0
        for line in self._lines:
            line_width, line_height = self._font.size(line)

            required_width = max(required_width, line_width)
            required_height += line_height + self._line_spacing

        self.rect.width = min(max_width, required_width)
        self.rect.height = min(max_height, required_height)

        self._required_width = required_width
        self._required_height = required_height

        return self.rect.size

    @property
    def fg(self) -> pg.Color:
        return self._fg

    @fg.setter
    def fg(self, value: pg.Color) -> None:
        self._fg = value
        self._needs_redraw = True

    @property
    def bg(self) -> pg.Color:
        return self._bg

    @bg.setter
    def bg(self, value: pg.Color) -> None:
        self._bg = value
        self._needs_redraw = True
