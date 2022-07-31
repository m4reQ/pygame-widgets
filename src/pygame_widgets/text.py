'''
Provides support for smart text rendering.
'''

import dataclasses
import enum
import itertools
import logging
import typing as t

import pygame as pg

from pygame_widgets.internal import ConfigBase, WidgetBase

_BlitTarget = t.Tuple[pg.surface.Surface, t.Tuple[int, int]]


class TextAlign(enum.Enum):
    '''
    An enum used in `TextConfig.align`.
    Represents alignment of text in a widget.
    '''

    LEFT = enum.auto()
    RIGHT = enum.auto()
    CENTER = enum.auto()


class TextFit(enum.Enum):
    FIT = enum.auto()
    EXPAND = enum.auto()


@dataclasses.dataclass
class TextConfig(ConfigBase):
    '''
    Configuration structure for
    `Text` widget.
    '''

    # pylint: disable=too-many-instance-attributes

    text_color: pg.Color = pg.Color(0, 0, 0, 255)
    bg_color: pg.Color = pg.Color(255, 255, 255, 0)
    align: TextAlign = TextAlign.LEFT
    font: pg.font.Font = pg.font.SysFont('Consolas', 24)
    use_antialiasing: bool = True
    line_spacing: int = 0
    tab_size: int = 4
    margin: pg.Rect = pg.Rect(0, 0, 0, 0)
    fit: TextFit = TextFit.FIT


class Text(WidgetBase):
    '''
    A widget that lets you display text with
    automatic handling of special characters (such as newline or tab) or
    text alignment.
    '''

    # pylint: disable=too-few-public-methods

    def __init__(self,
                 rect: pg.Rect,
                 text: str,
                 config: TextConfig = TextConfig()):
        super().__init__()

        self.rect = rect
        self.text = text
        self.config = config

        self.image = self._render_image()
        self.rect: pg.Rect = self.image.get_rect()

    def _render_image(self) -> pg.Surface:
        config = self.config
        font = config.font

        text = self.text.replace('\t', ' ' * config.tab_size)

        line_surfaces = [
            font.render(
                line,
                config.use_antialiasing,
                config.text_color)
            for line in text.split('\n')
        ]
        surfaces_count = len(line_surfaces)

        margin = config.margin

        text_img_height = sum(x.get_height() for x in line_surfaces)\
            + (surfaces_count - 1) * config.line_spacing\
            + margin.top + margin.height

        text_img_width = max(x.get_width() for x in line_surfaces)\
            + margin.left + margin.width

        uses_alpha = config.bg_color.a != 255 or config.text_color.a != 255
        text_img = pg.Surface(
            (text_img_width, text_img_height),
            pg.SRCALPHA if uses_alpha else 0)
        text_img.fill(pg.Color(255, 255, 255, 0))

        y_offsets = itertools.accumulate(
            (x.get_height() for x in line_surfaces),
            initial=margin.top)

        blit_target_create_func: t.Callable[[pg.surface.Surface, int, int], _BlitTarget] # noqa
        if self.config.align == TextAlign.LEFT:
            blit_target_create_func = self._create_blit_target_left
        elif self.config.align == TextAlign.RIGHT:
            blit_target_create_func = self._create_blit_target_right
        else:
            blit_target_create_func = self._create_blit_target_center

        blit_targets = [
            blit_target_create_func(
                surf,
                text_img.get_width(),
                y_offset + self.config.line_spacing * idx)
            for (idx, surf, y_offset)
            in zip(range(surfaces_count), line_surfaces, y_offsets)]

        text_img.blits(blit_targets, False)

        if config.fit == TextFit.FIT:
            _logger.warning('Using fit=TextFit.FIT forces text surface to resize leading to low text quality.') # noqa

            scale_size = (
                min(text_img.get_width(), self.rect.width),
                min(text_img.get_height(), self.rect.height))
            text_img = pg.transform.smoothscale(text_img, scale_size)

        if config.fit == TextFit.EXPAND:
            self.rect.width = min(text_img.get_width(), self.rect.width)
            self.rect.height = min(text_img.get_height(), self.rect.height)

        bg_img = pg.Surface(
            text_img.get_size(),
            pg.SRCALPHA if uses_alpha else 0)

        bg_img.fill(config.bg_color)
        bg_img.blit(text_img, (0, 0))

        return bg_img

    def _create_blit_target_left(self,
                                 surf: pg.surface.Surface,
                                 _,
                                 _y_offset: int) -> _BlitTarget:
        surf.set_alpha(self.config.text_color.a)

        return (
            surf,
            (
                self.config.margin.left,
                _y_offset))

    def _create_blit_target_right(self,
                                  surf: pg.surface.Surface,
                                  img_width: int,
                                  y_offset: int) -> _BlitTarget:
        surf.set_alpha(self.config.text_color.a)

        return (
            surf,
            (
                img_width - surf.get_width() - self.config.margin.width,
                y_offset))

    def _create_blit_target_center(self,
                                   surf: pg.surface.Surface,
                                   img_width: int,
                                   y_offset: int) -> _BlitTarget:
        surf.set_alpha(self.config.text_color.a)

        margin = self.config.margin
        width = img_width - margin.left - margin.width
        return (
            surf,
            (
                (width - surf.get_width()) // 2 + margin.left,
                y_offset))


# TODO: Move logging to config validation
_logger = logging.getLogger(__name__)
