'''
Provides support for better tasks completion
progress display.
'''

import dataclasses
import math
import typing as t

import pygame as pg

from pygame_widgets.internal import ConfigBase, StateHandle, WidgetBase


@dataclasses.dataclass
class ProgressBarConfig(ConfigBase):
    '''
    Configuration structure for
    `ProgressBar` widget.
    '''

    bg_color: pg.Color = pg.Color(0, 0, 0, 255)
    bar_color: pg.Color = pg.Color(0, 255, 0, 255)
    bar_image: t.Optional[pg.Surface] = None
    use_progress_as_mask: bool = False


class ProgressBar(WidgetBase, StateHandle[int]):
    '''
    A widget that lets you display current
    state of some tasks like loading resources in form
    of a nice progress bar.
    '''

    def __init__(self,
                 rect: pg.Rect,
                 max_progress: int,
                 config: ProgressBarConfig = ProgressBarConfig()) -> None:
        super().__init__()

        self.config = config
        self.rect: pg.Rect = rect
        self.max_progress = max_progress

        self.state = 0

        self._bg_image = self._render_bg_image()
        self._bar_image = self._render_bar_image()
        self.image = self._bg_image

    def redraw(self) -> None:
        bar_width = min(
            math.ceil(self.rect.width / self.max_progress * self.state),
            self.rect.width)

        self.image = self._bg_image
        self.image.blit(self._bar_image.subsurface(
            0,
            0,
            bar_width,
            self.rect.height),
            (0, 0))
        self.dirty = 1

    def increment_progress(self) -> None:
        '''
        Increments current progress by one.
        '''

        if self.state >= self.max_progress:
            return

        self.state += 1
        self.redraw()

    def reset_progress(self) -> None:
        '''
        Sets current progress to zero.
        '''

        self.state = 0
        if self.state_changed:
            self.redraw()

    @property
    def progress(self) -> int:
        '''
        Current progress.
        '''

        return self.state

    def _render_bar_image(self) -> pg.Surface:
        bar_image = self.config.bar_image
        bg_color = self.config.bg_color
        rect = self.rect

        img: pg.Surface
        if bar_image:
            if bar_image.get_size() != rect.size:
                img = pg.transform.smoothscale(bar_image, rect.size)
            else:
                img = bar_image
        else:
            img = pg.Surface(
                rect.size,
                pg.SRCALPHA if bg_color.a != 255 else 0)
            img.fill(bg_color, pg.Rect(0, 0, *img.get_size()))

        return img

    def _render_bg_image(self) -> pg.Surface:
        img = pg.Surface(
            self.rect.size,
            pg.SRCALPHA if self.config.bg_color.a != 255 else 0)
        img.fill(self.config.bg_color)

        return img
