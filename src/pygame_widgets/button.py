'''
Adds button widgets.
'''

import dataclasses
import typing as t
import enum

import pygame as pg


class ButtonState(enum.Enum):
    '''
    An enum used in `Button.state` and
    `ButtonConfig.default_state`.
    Represents current state of the button widget.
    '''

    OFF = enum.auto()
    HOVER = enum.auto()
    CLICK = enum.auto()
    DISABLED = enum.auto()


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
    background_image: t.Optional[pg.Surface] = None
    highlight_on_hover: bool = False
    center_text: bool = False
    default_state: ButtonState = ButtonState.OFF
    collide_on_mask: bool = False
    activate_button: int = 0
    on_click: t.Callable = lambda: None
    on_hover: t.Callable = lambda: None


class Button(pg.sprite.Sprite):
    '''
    A simple button that can use image as a background
    and have different properties based on its current
    state. It also provides an ability to hook callbacks
    to state changes.
    '''

    # pylint: disable=too-many-instance-attributes

    def __init__(self, rect: pg.Rect, config: ButtonConfig):
        super().__init__()

        self.config = config
        self.rect = rect

        self._state = config.default_state
        self._prev_state = self._state
        self._on_click_func = config.on_click
        self._on_hover_func = config.on_hover
        self._inactive_image = self._render_image(False)
        self._active_image = self._render_image(True)

        self.image = self._inactive_image

        self._create_mask()

        self.dirty = 1

    def update(self, *args: t.Any, **kwargs: t.Any) -> None:
        # pylint: disable=missing-function-docstring
        super().update(*args, **kwargs)

        if self._state == ButtonState.DISABLED:
            return

        self._get_new_state()

        state = self._state
        prev_state = self._prev_state

        if state == prev_state:
            return

        if state == ButtonState.HOVER and prev_state != ButtonState.CLICK:
            if self.config.highlight_on_hover:
                self._on_hover_func()
                self.image = self._active_image
            else:
                self.image = self._inactive_image
        elif state == ButtonState.CLICK:
            self.image = self._active_image
            self._on_click_func()
        elif state == ButtonState.OFF:
            self.image = self._inactive_image

        self.dirty = 1
        self._prev_state = state

    def _get_new_state(self):
        rect = t.cast(pg.Rect, self.rect)

        mouse_pos = pg.mouse.get_pos()
        collision = False
        if rect.collidepoint(mouse_pos):
            collision = self.mask.get_at((
                mouse_pos[0] - rect.x,
                mouse_pos[1] - rect.y)) != 0

        if collision:
            click = pg.mouse.get_pressed()[self.config.activate_button]
            if click:
                self._state = ButtonState.CLICK
            else:
                self._state = ButtonState.HOVER
        else:
            self._state = ButtonState.OFF

    def _create_mask(self) -> None:
        if self.config.collide_on_mask:
            self.mask = pg.mask.from_surface(
                t.cast(pg.Surface, self.image),
                threshold=0)
        else:
            self.mask = pg.mask.Mask(
                t.cast(pg.Rect, self.rect).size,
                fill=True)

    def _render_image(self, active: bool) -> pg.Surface:
        rect = t.cast(pg.Rect, self.rect)
        config = self.config

        img: pg.Surface
        if config.background_image:
            img = pg.transform.smoothscale(config.background_image, rect.size)
        else:
            img = pg.Surface(rect.size, pg.SRCALPHA)

        bg_color: pg.Color
        if active:
            bg_color = config.bg_color_active
        else:
            bg_color = config.bg_color_inactive

        img.fill(bg_color, special_flags=pg.BLEND_RGBA_MULT)

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
            text_color
        )

        text_pos = (0, 0)
        if config.center_text:
            text_pos = (
                (img.get_width() - text.get_width()) // 2,
                (img.get_height() - text.get_height()) // 2,
            )

        img.blit(text, text_pos)

        return img

    @property
    def state(self) -> ButtonState:
        '''
        Current state of the button.
        '''

        return self._state

    @state.setter
    def state(self, value: ButtonState) -> None:
        self._state = value
