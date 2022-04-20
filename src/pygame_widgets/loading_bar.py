'''
Provides support for better tasks completion
progress display.
'''

import dataclasses
import typing as t
import math

import pygame as pg

@dataclasses.dataclass
class ProgressBarConfig:
    '''
    Configuration structure for
    `ProgressBar` widget.
    '''

    bg_color: pg.Color = pg.Color(0, 0, 0, 255)
    bar_color: pg.Color = pg.Color(0, 255, 0, 255)
    bar_image: t.Optional[pg.Surface] = None

class ProgressBar(pg.sprite.DirtySprite):
    '''
    A widget that lets you display current
    state of some tasks like loading resources in form
    of a nice progress bar.
    '''

    def __init__(self,
                 rect: pg.Rect,
                 max_progress: int,
                 config: ProgressBarConfig) -> None:
        super().__init__()

        self.config = config
        self.rect = rect
        self.max_progress = max_progress

        self._bar_image: t.Optional[pg.Surface] = None
        if config.bar_image:
            self._bar_image = pg.transform.smoothscale(config.bar_image, self.rect.size)

        self._progress = 0

        self._render_image()

    def _render_image(self) -> None:
        rect = t.cast(pg.Rect, self.rect)

        self.image = pg.Surface(rect.size, pg.SRCALPHA)
        self.image.fill(self.config.bg_color)

        bar_width = min(
            math.ceil(rect.width / self.max_progress * self._progress),
            rect.width)

        bar: pg.Surface
        if self._bar_image:
            bar = self._bar_image.subsurface(0, 0, bar_width, rect.height)
        else:
            bar = pg.Surface((bar_width, rect.height), pg.SRCALPHA)
            bar.fill(self.config.bar_color)

        self.image.blit(bar, (0, 0))

        self.dirty = 1

    def increment_progress(self) -> None:
        '''
        Increments current progress by one.
        '''

        if self._progress >= self.max_progress:
            return

        self._progress += 1
        self._render_image()

    def reset_progress(self) -> None:
        '''
        Sets current progress to zero.
        '''

        self._progress = 0
        self._render_image()

    @property
    def progress(self) -> int:
        '''
        Current progress.
        '''

        return self._progress
