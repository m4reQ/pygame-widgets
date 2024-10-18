import uuid

import pygame as pg

from guinea import _internal
from guinea._internal import TargetFill
from guinea.enums import TextAlign, TextFit
from guinea.shaders import Shader
from guinea.widget import Widget

_BlitTarget = tuple[pg.Surface, tuple[int, int]]

class Text(Widget):
    DEFAULT_FONT_SIZE = 24
    DEFAULT_FG_COLOR = pg.Color(0, 0, 0, 255)

    def __init__(self,
                 text: str,
                 *,
                 fg: TargetFill = DEFAULT_FG_COLOR,
                 bg: TargetFill | None = None,
                 font: pg.font.Font | None = None,
                 antialiasing: bool = True,
                 line_spacing: int = 0,
                 tab_size: int = 4,
                 fit: TextFit = TextFit.FIT,
                 align: TextAlign = TextAlign.LEFT,
                 _id: uuid.UUID | None = None,
                 rect: pg.Rect | None = None) -> None:
        super().__init__(_id, rect)

        self._lines = _split_text_lines(text, tab_size)
        self._fg = fg
        self._bg = bg
        self._align = align
        self._font = font or _internal.FontCache.get_default_of_size(Text.DEFAULT_FONT_SIZE)
        self._antialiasing = antialiasing
        self._line_spacing = line_spacing
        self._tab_size = tab_size
        self._fit = fit

        self._required_width = 0
        self._required_height = 0

        self.image = pg.Surface((0, 0))

    def _render_line(self, line: str) -> pg.Surface:
        if isinstance(self._fg , pg.Color):
            return self._font.render(
                line,
                self._antialiasing,
                self._fg)

        return self._font.render(
            line,
            self._antialiasing,
            (255, 255, 255, 255))

    def _fit_image(self, img: pg.Surface) -> pg.Surface:
        target_size = (
            min(self._required_width, self.rect.width),
            min(self._required_height, self.rect.height))

        if self._fit == TextFit.FIT:
            return pg.transform.smoothscale(img, target_size)

        return self.image.subsurface((0, 0), target_size)

    def _get_x_alignment(self, avail_width: int, width: int) -> int:
        if self._align == TextAlign.RIGHT:
            return avail_width - width
        elif self._align == TextAlign.CENTER:
            return _internal.divide_with_overflow(avail_width - width, 2)

        # TextAlign.LEFT
        return 0

    def _generate_blit_targets(self) -> list[_BlitTarget]:
        current_y = 0
        targets: list[_BlitTarget] = []

        for line in self._lines:
            line_surf = self._render_line(line)
            pos = (
                self._get_x_alignment(self._required_width, line_surf.get_width()),
                current_y)
            targets.append((line_surf, pos))

            current_y += line_surf.get_height() + self._line_spacing

        return targets

    def redraw(self) -> None:
        # render text background
        surface_flags = 0
        if self._bg is None:
            surface_flags = pg.SRCALPHA
        else:
            surface_flags = _internal.get_surface_flags_for_target_fill(self._bg)
        src_img = pg.Surface(
            (self._required_width, self._required_height),
            surface_flags)

        if self._bg is not None:
            if isinstance(self._bg, pg.Color):
                src_img.fill(self._bg)
            elif isinstance(self._bg, pg.Surface):
                src_img.blit(
                    pg.transform.smoothscale(self._bg, src_img.get_size()),
                    (0, 0))
            else: # isinstance(self._bg, Shader)
                self._bg.draw(src_img, False)

        # render text
        targets = self._generate_blit_targets()
        if isinstance(self._fg, pg.Color):
            src_img.blits(targets)
        else:
            text_img = pg.Surface(src_img.get_size(), pg.SRCALPHA)
            text_img.blits(targets)

            if isinstance(self._fg, pg.Surface):
                text_img.blit(
                pg.transform.smoothscale(self._fg, text_img.get_size()),
                (0, 0),
                special_flags=pg.BLEND_RGBA_MIN)
            else: # isinstance(self._fg, Shader)
                self._fg.draw(text_img, True)

            src_img.blit(text_img, (0, 0))

        # crop image according to used text
        if self._required_width > self.rect.width or self._required_height > self.rect.height:
            src_img = self._fit_image(src_img)

        self.image = src_img

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

def _split_text_lines(text: str, tab_size: int) -> list[str]:
    return [x for x in text.replace('\t', ' ' * tab_size).split('\n') if x != '']
