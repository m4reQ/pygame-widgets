'''
Provides support for smart text rendering.
'''

from __future__ import annotations

import typing as t
import dataclasses
import enum
import itertools

import pygame as pg

pg.font.init()

_BlitTarget = t.Tuple[pg.surface.Surface, t.Tuple[int, int]]

class TextAlign(enum.Enum):
    '''
    An enum used in `TextConfig.align`.
    Represents alignment of text in a widget.
    '''

    LEFT = enum.auto()
    RIGHT = enum.auto()
    CENTER = enum.auto()

@dataclasses.dataclass
class TextConfig:
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

class Text(pg.sprite.DirtySprite):
    '''
    A widget that lets you display text with
    automatic handling of special characters (such as newline or tab) or
    text alignment.
    '''

    # pylint: disable=too-few-public-methods

    def __init__(self, pos: t.Tuple[int, int], text: str, config: TextConfig):
        super().__init__()

        self.text = text
        self.config = config

        self._render_image()
        self.rect = pg.Rect(pos[0], pos[1], *t.cast(pg.Surface, self.image).get_size())

        self.dirty = 1

    def _render_image(self) -> None:
        font = self.config.font
        text = self.text.replace('\t', ' ' * self.config.tab_size)

        line_surfaces = [
            font.render(
                line,
                self.config.use_antialiasing,
                self.config.text_color)
            for line in text.split('\n')
        ]
        surfaces_count = len(line_surfaces)

        margin = self.config.margin

        img_height = sum(x.get_height() for x in line_surfaces)\
            + (surfaces_count - 1) * self.config.line_spacing\
            + margin.top + margin.height

        img_width = max(x.get_width() for x in line_surfaces)\
            + margin.left + margin.width

        self.image = pg.Surface((img_width, img_height), flags=pg.SRCALPHA)
        if self.config.bg_color:
            self.image.fill(self.config.bg_color)

        y_offsets = itertools.accumulate(
            (x.get_height() for x in line_surfaces),
            initial=margin.top)

        blit_target_create_func: t.Callable[[pg.surface.Surface, int], _BlitTarget]
        if self.config.align == TextAlign.LEFT:
            blit_target_create_func = self._create_blit_target_left
        elif self.config.align == TextAlign.RIGHT:
            blit_target_create_func = self._create_blit_target_right
        elif self.config.align == TextAlign.CENTER:
            blit_target_create_func = self._create_blit_target_center
        else:
            assert False, 'unreachable'

        blit_targets = [
            blit_target_create_func(surf, y_offset + self.config.line_spacing * idx)
            for (idx, surf, y_offset)
            in zip(range(surfaces_count), line_surfaces, y_offsets)]
        self.image.blits(blit_targets, False) #type: ignore

    def _create_blit_target_left(self, surf: pg.surface.Surface, _y_offset: int) -> _BlitTarget:
        return (
            surf,
            (
                self.config.margin.left,
                _y_offset)
            )

    def _create_blit_target_right(self, surf: pg.surface.Surface, _y_offset: int) -> _BlitTarget:
        width = t.cast(pg.Surface, self.image).get_width()
        return (
            surf,
            (
                width - surf.get_width() - self.config.margin.width,
                _y_offset)
            )

    def _create_blit_target_center(self, surf: pg.surface.Surface, _y_offset: int) -> _BlitTarget:
        margin = self.config.margin
        width = t.cast(pg.Surface, self.image).get_width() - margin.left - margin.width
        return (
            surf,
            (
                (width - surf.get_width()) // 2 + margin.left,
                _y_offset)
            )
