# TODO: Add documentation # noqa
import dataclasses
import typing as t

import pygame as pg

from pygame_widgets import utils
from pygame_widgets.widget import StateHandle, WidgetBase


@dataclasses.dataclass
class RadioButtonConfig:
    '''
    Configuration structure for `RadioButton` widget.
    '''

    color: pg.Color = pg.Color(255, 255, 255, 255)
    active_image: pg.Surface | None = None
    inactive_image: pg.Surface | None = None
    activate_button: int = 0
    collide_on_mask: bool = True
    on_click: t.Callable[[], t.Any] = lambda: None


class RadioButton(WidgetBase, StateHandle[bool]):
    def __init__(self,
                 rect: pg.Rect,
                 config: RadioButtonConfig = RadioButtonConfig()) -> None:
        super().__init__([(pg.MOUSEBUTTONDOWN, self._mouse_click_cb)])

        self.config = config
        self.rect: pg.Rect = rect
        self.mask = self._create_mask() if config.collide_on_mask else None

        self._active_image = self._render_active_image()
        self._inactive_image = self._render_inactive_image()
        self._is_active = False

        self.image = self._inactive_image

        self.state = False

    @property
    def is_on(self) -> bool:
        '''
        Current state of the button.
        '''

        return self.state

    @is_on.setter
    def is_on(self, value: bool) -> None:
        self.state = value
        if self.state_changed:
            self.redraw()

    def _render_inactive_image(self) -> pg.Surface:
        config = self.config
        rect = self.rect

        if config.inactive_image:
            return config.inactive_image
        else:
            side = min(rect.size)
            img = pg.Surface((side, side), pg.SRCALPHA)
            width = int(side // 10)
            center = img.get_rect().center

            pg.draw.circle(img, config.color, center, (side // 2), width)

            return img

    def _render_active_image(self) -> pg.Surface:
        config = self.config
        rect = self.rect

        if config.active_image:
            return config.active_image
        else:
            side = min(rect.size)
            img = pg.Surface((side, side), pg.SRCALPHA)
            width = int(side // 10)
            center = img.get_rect().center

            pg.draw.circle(
                img,
                config.color,
                center,
                (side // 2),
                width)
            pg.draw.circle(
                img,
                config.color,
                center,
                (side // 2) - width * 2)

            return img

    def _create_mask(self) -> pg.Mask:
        side = min(self.rect.size)

        img = pg.Surface((side, side), pg.SRCALPHA)
        img.fill(pg.Color(0, 0, 0, 0))
        pg.draw.circle(
            img,
            pg.Color(255, 255, 255, 255),
            img.get_rect().center,
            (side // 2))

        return pg.mask.from_surface(img, threshold=0)

    def _mouse_click_cb(self, e: pg.event.Event) -> None:
        collision = utils.collide_point(e.pos, self.rect, self.mask)
        if not collision:
            return

        self.state = not self.state
        self.redraw()

    def redraw(self) -> None:
        if self.state:
            self.image = self._active_image
        else:
            self.image = self._inactive_image

        self.dirty = 1
