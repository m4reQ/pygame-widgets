'''
Provides support for better tasks completion
progress display.
'''

import dataclasses
import math

import pygame as pg

from pygame_widgets.widget import WidgetBase


@dataclasses.dataclass
class ProgressBarConfig:
    '''
    Configuration structure for
    `ProgressBar` widget.
    '''

    bg_color: pg.Color = pg.Color(0, 0, 0, 255)
    bar_color: pg.Color = pg.Color(0, 255, 0, 255)
    bar_image: pg.Surface | None = None
    use_progress_as_mask: bool = False


class ProgressBar(WidgetBase):
    '''
    A widget that lets you display current
    state of some tasks like loading resources in form
    of a nice progress bar.
    '''

    def __init__(self,
                 rect: pg.Rect,
                 max_progress: int,
                 config: ProgressBarConfig=ProgressBarConfig()):
        super().__init__()

        self.config = config
        self.rect: pg.Rect = rect
        self.max_progress = max_progress

        self._progress = 0

        self._bg_image = self._render_bg_image()
        self.image = self._bg_image

    def _render_bg_image(self) -> pg.Surface:
        bg_color = self.config.bg_color
        bar_image = self.config.bar_image

        img: pg.Surface
        if bar_image:
            if bar_image.get_size() != self.rect.size:
                img = pg.transform.smoothscale(bar_image, self.rect.size)
            else:
                img = bar_image
        else:
            img = pg.Surface(self.rect.size, pg.SRCALPHA if bg_color.a != 255 else 0)
            img.fill(bg_color, pg.Rect(0, 0, *img.get_size()))

        return img

    def redraw(self) -> None:
        super().redraw()

        bar_width = min(
            math.ceil(self.rect.width / self.max_progress * self._progress),
            self.rect.width)

        if self.config.use_progress_as_mask:
            self.image = self._bg_image.subsurface(0, 0, bar_width, self.rect.height)
        else:
            self.image = self._bg_image

            bar_color = self.config.bar_color

            bar_image = pg.Surface((bar_width, self.rect.height), pg.SRCALPHA if bar_color.a != 255 else 0)
            bar_image.fill(bar_color)
            self.image.blit(bar_image, (0, 0))

    def increment_progress(self) -> None:
        '''
        Increments current progress by one.
        '''

        if self._progress >= self.max_progress:
            return

        self._progress += 1
        self.needs_redraw = True

    def reset_progress(self) -> None:
        '''
        Sets current progress to zero.
        '''

        self._progress = 0
        self.needs_redraw = True

    @property
    def progress(self) -> int:
        '''
        Current progress.
        '''

        return self._progress
