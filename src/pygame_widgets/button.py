'''
Adds button widgets.
'''

import dataclasses
import typing as t

import pygame as pg

from pygame_widgets import internal
from pygame_widgets.widget import WidgetBase

pg.font.init()

@dataclasses.dataclass
class ButtonConfig:
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
    background_image: pg.Surface | None = None
    activate_on_hover: bool = False
    center_text: bool = False
    is_disabled: bool = False
    collide_on_mask: bool = False
    activate_button: int = 1
    on_click: t.Callable[[], t.Any] = lambda: None
    on_hover: t.Callable[[], t.Any] = lambda: None
    on_release: t.Callable[[], t.Any] = lambda: None


class Button(WidgetBase):
    '''
    A simple button that can use image as a background
    and have different properties based on its current
    state. It also provides an ability to hook callbacks
    to state changes.
    '''

    # pylint: disable=too-many-instance-attributes

    def __init__(self, rect: pg.Rect, config: ButtonConfig=ButtonConfig()):
        super().__init__()

        self.config = config
        self.rect: pg.Rect = rect

        self._cursor_in_box = False
        self._is_clicked = False
        self._is_disabled = config.is_disabled
        self._activate_button = config.activate_button
        self._activate_on_hover = config.activate_on_hover

        self._on_click_func = config.on_click
        self._on_hover_func = config.on_hover
        self._on_release_func = config.on_release

        self._inactive_image = self._render_image(False)
        self._active_image = self._render_image(True)

        self.image = self._inactive_image

        self.mask: pg.Mask | None = None
        if config.collide_on_mask:
            self.mask = pg.mask.from_surface(
                self.image,
                threshold=0)

        internal.add_event_handler(pg.MOUSEBUTTONDOWN, self._mouse_click_cb)
        internal.add_event_handler(pg.MOUSEBUTTONUP, self._mouse_release_cb)
        internal.add_event_handler(pg.MOUSEMOTION, self._cursor_move_cb)

    def _render_image(self, active: bool) -> pg.Surface:
        config = self.config

        img: pg.Surface
        if config.background_image:
            img = pg.transform.smoothscale(config.background_image, self.rect.size)
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
        if self._is_disabled:
            return

        cursor_in_box = self._check_cursor_in_box(event.pos)
        if not cursor_in_box and self._cursor_in_box:
            self._hover = False
        elif cursor_in_box and not self._cursor_in_box:
            internal.schedule_call(self._on_hover_func)
            self._hover = True
        else:
            return

        self._cursor_in_box = cursor_in_box

    def _mouse_click_cb(self, event: pg.event.Event) -> None:
        if self._is_disabled:
            return

        if event.button != self._activate_button or not self._cursor_in_box:
            return

        if self._on_click_func:
            internal.schedule_call(self._on_click_func)

        self._is_clicked = True
        self.needs_redraw = True

    def _mouse_release_cb(self, event: pg.event.Event) -> None:
        if self._is_disabled:
            return

        if event.button != self._activate_button or not self._is_clicked:
            return

        if self._on_release_func:
            internal.schedule_call(self._on_release_func)

        self._is_clicked = False
        self.needs_redraw = True

    def redraw(self) -> None:
        super().redraw()

        if self._activate_on_hover:
            if self._hover:
                self.image = self._active_image
            else:
                self.image = self._inactive_image

            return

        if self._is_clicked:
            self.image = self._active_image
        else:
            self.image = self._inactive_image

    def _check_cursor_in_box(self, pos: tuple[int, int]) -> bool:
        if self.mask:
            pos = (
                pos[0] - self.rect.x,
                pos[1] - self.rect.y)
            return self.mask.get_at(pos) != 0

        return self.rect.collidepoint(pos)

    def set_enabled(self, value: bool) -> None:
        self._is_disabled = not value
