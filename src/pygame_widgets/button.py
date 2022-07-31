'''
Adds button widgets.
'''

import dataclasses
import enum
import typing as t

import pygame as pg

from pygame_widgets import utils
from pygame_widgets.internal import ConfigBase, StateHandle, WidgetBase


@dataclasses.dataclass
class ButtonConfig(ConfigBase):
    '''
    Configuration structure for
    `Button` widget.
    '''

    # pylint: disable=too-many-instance-attributes

    text_active: str = ''
    text_inactive: str = ''
    text_color_active: pg.Color = pg.Color(0, 0, 0, 255)
    text_color_inactive: pg.Color = pg.Color(0, 0, 0, 255)
    font: pg.font.Font = pg.font.SysFont('Consolas', 24)
    bg_color_active: pg.Color = pg.Color(255, 255, 255, 255)
    bg_color_inactive: pg.Color = pg.Color(255, 255, 255, 255)
    background_image: t.Optional[pg.Surface] = None
    activate_on_hover: bool = False
    center_text: bool = False
    is_disabled: bool = False
    collide_on_mask: bool = False
    activate_button: int = 1
    on_click: t.Callable[[], t.Any] = lambda: None
    on_hover: t.Callable[[], t.Any] = lambda: None
    on_release: t.Callable[[], t.Any] = lambda: None


class _ButtonState(enum.Enum):
    ACTIVE = enum.auto()
    INACTIVE = enum.auto()
    HOVER = enum.auto()


class Button(WidgetBase, StateHandle[_ButtonState]):
    '''
    A simple button that can use image as a background
    and have different properties based on its current
    state. It also provides an ability to hook callbacks
    to state changes.
    '''

    # pylint: disable=too-many-instance-attributes

    def __init__(self, rect: pg.Rect, config: ButtonConfig = ButtonConfig()):
        super().__init__([
            (pg.MOUSEBUTTONDOWN, self._mouse_click_cb),
            (pg.MOUSEBUTTONUP, self._mouse_release_cb),
            (pg.MOUSEMOTION, self._cursor_move_cb)])

        self.config = config
        self.rect: pg.Rect = rect

        self._is_disabled = config.is_disabled
        self._activate_button = config.activate_button
        self._activate_on_hover = config.activate_on_hover

        self._on_click_func = config.on_click
        self._on_hover_func = config.on_hover
        self._on_release_func = config.on_release

        self._inactive_image = self._render_image(False)
        self._active_image = self._render_image(True)

        self.image = self._inactive_image
        self.mask = pg.mask.from_surface(self.image, threshold=0) if config.collide_on_mask else None # noqa

        self.state = _ButtonState.INACTIVE

    def _render_image(self, active: bool) -> pg.Surface:
        config = self.config

        img: pg.Surface
        if config.background_image:
            img = pg.transform.smoothscale(
                config.background_image,
                self.rect.size)
        else:
            img = pg.Surface(self.rect.size, pg.SRCALPHA)

        bg_color: pg.Color
        if active:
            bg_color = config.bg_color_active
        else:
            bg_color = config.bg_color_inactive

        img.fill(bg_color)

        text_color: pg.Color
        text_str: str
        if active:
            text_color = config.text_color_active
            text_str = config.text_active
        else:
            text_color = config.text_color_inactive
            text_str = config.text_inactive

        text = config.font.render(
            text_str,
            True,
            text_color)

        text_pos = (0, 0)
        if config.center_text:
            text_pos = (
                (img.get_width() - text.get_width()) // 2,
                (img.get_height() - text.get_height()) // 2)

        img.blit(text, text_pos)

        return img

    def _cursor_move_cb(self, event: pg.event.Event) -> None:
        if self._is_disabled or self.state == _ButtonState.ACTIVE:
            return

        collision = utils.collide_point(event.pos, self.rect, self.mask)
        if collision:
            if self._on_hover_func:
                self._on_hover_func()

            self.state = _ButtonState.HOVER
        else:
            self.state = _ButtonState.INACTIVE

        # TODO: Remove unnecessary draw getting called when transitioning
        # from hover to inactive even if _activate_on_hover
        # is set to False (no change in image)
        if self.state_changed:
            self.redraw()

    def _mouse_click_cb(self, event: pg.event.Event) -> None:
        if self._is_disabled:
            return

        collision = utils.collide_point(event.pos, self.rect, self.mask)
        if not collision or event.button != self._activate_button:
            return

        if self._on_click_func:
            self._on_click_func()

        self.state = _ButtonState.ACTIVE
        if self.state_changed:
            self.redraw()

    def _mouse_release_cb(self, event: pg.event.Event) -> None:
        if self._is_disabled or event.button != self._activate_button:
            return

        if self._on_release_func:
            self._on_release_func()

        self.state = _ButtonState.INACTIVE
        if self.state_changed:
            self.redraw()

    def redraw(self) -> None:
        if self.state == _ButtonState.INACTIVE:
            self.image = self._inactive_image
            self.dirty = 1
        elif self.state == _ButtonState.ACTIVE or (self.state == _ButtonState.HOVER and self._activate_on_hover): # noqa
            self.image = self._active_image
            self.dirty = 1

    def set_enabled(self, value: bool) -> None:
        self._is_disabled = not value
