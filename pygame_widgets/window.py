import uuid
from typing import Any

import pygame as pg

from pygame_widgets import _internal, events
from pygame_widgets.enums import Side
from pygame_widgets.widget import (ContainerWidget, SingleChildContainerWidget,
                                   Widget)

RESIZE_RECT_TOLERANCE = 2
TITLE_OFFSET = 2
BORDER_THICKNESS = 1
BUTTON_WIDTH_FACTOR = 0.4
TITLE_FONT_SIZE = 18

DEFAULT_TITLE_BG = pg.Color(186, 186, 186)
DEFAULT_WINDOW_BG = pg.Color(222, 222, 222)
DEFAULT_TITLE_FG = pg.Color(0, 0, 0)
DEFAULT_BORDER_COLOR = pg.Color(66, 66, 66)
DEFAULT_BUTTON_HIGHLIGHT_COLOR = pg.Color(227, 227, 227)

class Window(Widget):
    _grab_lock = False

    def __init__(self,
                 child: Widget,
                 title: str,
                 rect: pg.Rect,
                 *,
                 title_fg: pg.Color = DEFAULT_TITLE_FG,
                 title_bg: pg.Color = DEFAULT_TITLE_BG,
                 window_bg: pg.Color = DEFAULT_WINDOW_BG,
                 border_color: pg.Color = DEFAULT_BORDER_COLOR,
                 button_highlight_color: pg.Color = DEFAULT_BUTTON_HIGHLIGHT_COLOR,
                 title_font: pg.font.Font | None = None,
                 _id: uuid.UUID | None = None) -> None:
        super().__init__(_id, rect)

        self.child = child
        child.set_parent(self) # type: ignore

        self.visible = True
        self.image = pg.Surface((0, 0))

        self._inner_group: pg.sprite.LayeredUpdates = pg.sprite.LayeredUpdates()
        Widget.register_widget_stack(self._inner_group, child)

        self._title_font = title_font or _internal.FontCache.get_default_of_size(TITLE_FONT_SIZE)
        self._title = title
        self._title_fg = title_fg
        self._title_bg = title_bg
        self._window_bg = window_bg
        self._border_color = border_color
        self._button_highlight_color = button_highlight_color

        self._minimize_btn_collide_rect = pg.Rect(0, 0, 0, 0)
        self._close_btn_collide_rect = pg.Rect(0, 0, 0, 0)

        self._btn_width = 0
        self._btn_margin = 0

        self._title_bar_rect = pg.Rect(0, 0, 0, 0)
        self._child_rect = pg.Rect(0, 0, 0, 0)

        self.is_moving = False
        self.resize_side: Side | None = None
        self._border_collide_rects = list[tuple[pg.Rect, Side]]()

        self._highlight_minimize_btn = False
        self._highlight_close_btn = False

        self._is_minimized = False

        events.register_handler(pg.MOUSEBUTTONDOWN, self._mouse_button_down_callback)
        events.register_handler(pg.MOUSEMOTION, self._mouse_move_callback)
        events.register_handler(pg.MOUSEBUTTONUP, self._mouse_button_up_callback)

    def _mouse_button_up_callback(self, _: pg.event.Event) -> None:
        Window._grab_lock = False

        self.is_moving = False
        self.resize_side = None

    def _mouse_move_callback(self, event: pg.event.Event) -> None:
        # handle window move
        if self.is_moving:
            self.rect.move_ip(event.rel)
            self._needs_redraw = True
            self._needs_reposition = True

        # handle button highlights
        highlight_minimize_btn = self._minimize_btn_collide_rect.collidepoint(event.pos)
        if highlight_minimize_btn != self._highlight_minimize_btn:
            self._highlight_minimize_btn = highlight_minimize_btn
            self._needs_redraw = True

        highlight_close_btn = self._close_btn_collide_rect.collidepoint(event.pos)
        if highlight_close_btn != self._highlight_close_btn:
            self._highlight_close_btn = highlight_close_btn
            self._needs_redraw = True

        # handle window resize
        if self.resize_side is not None:
            assert self.resize_side != Side.TOP, 'Resizing window from top is not possible (this is a bug)'

            match self.resize_side:
                case Side.LEFT:
                    self.rect.left += event.rel[0]
                    self.rect.width -= event.rel[0]
                case Side.RIGHT:
                    self.rect.width += event.rel[0]
                case Side.BOTTOM:
                    self.rect.height += event.rel[1]

            self._needs_redraw = True
            self._needs_reposition = True

    def _mouse_button_down_callback(self, event: pg.event.Event) -> None:
        # handle close button collision
        if self._close_btn_collide_rect.collidepoint(event.pos):
            self.kill()

            # return early to prevent moving already deleted window
            return

        # handle minimize button collision
        if self._minimize_btn_collide_rect.collidepoint(event.pos):
            self._is_minimized = not self._is_minimized
            self.child.set_visible(not self._is_minimized)

            self._needs_redraw = True
            self._needs_reposition = True

        # handle move collision
        if self._title_bar_rect.collidepoint(event.pos) and not Window._grab_lock:
            Window._grab_lock = True

            self.is_moving = True

            groups = self.groups()
            assert len(groups) == 1, 'Window does not support usage within multiple sprite groups'

            group = groups[0]
            assert isinstance(group, pg.sprite.LayeredUpdates), 'Window requires to be placed inside sprite group that supports LayeredUpdates'

            top_layer = group.get_top_layer()
            self.set_layer(top_layer)

        # handle resize collision
        if not self._is_minimized:
            for rect, side in self._border_collide_rects:
                if rect.collidepoint(event.pos):
                    self.resize_side = side
                    break

    def redraw(self) -> None:
        self.image = pg.Surface(self.rect.size, pg.SRCALPHA)

        title_bar_rect_abs = pg.Rect(
            0,
            0,
            self._title_bar_rect.width,
            self._title_bar_rect.height)

        # draw backgrounds
        if not self._is_minimized:
            self.image.fill(self._window_bg)

        self.image.fill(self._title_bg, rect=title_bar_rect_abs)

        # draw borders
        if not self._is_minimized:
            pg.draw.rect(
                self.image,
                self._border_color,
                self.image.get_rect(),
                width=BORDER_THICKNESS)

        pg.draw.rect(
            self.image,
            self._border_color,
            title_bar_rect_abs,
            width=BORDER_THICKNESS)

        # draw highlights
        if self._highlight_minimize_btn:
            pg.draw.circle(
                self.image,
                self._button_highlight_color,
                (self._btn_width // 2 + self._btn_margin, self._btn_width // 2 + self._btn_margin),
                self._btn_width)

        if self._highlight_close_btn:
            pg.draw.circle(
                self.image,
                self._button_highlight_color,
                (self.rect.width - self._btn_width // 2 - self._btn_margin, self._btn_width // 2 + self._btn_margin),
                self._btn_width)

        # draw title
        title_surf = self._title_font.render(self._title, True, self._title_fg, self._title_bg)
        self.image.blit(title_surf, (self._btn_margin * 2 + self._btn_width, TITLE_OFFSET))

        # draw buttons
        minimize_btn_img = _get_minimize_btn_img(self._is_minimized, self._btn_width)
        self.image.blit(minimize_btn_img, (self._btn_margin, self._btn_margin))

        close_btn_img = _internal._ImageCache.try_get_image('./assets/window_close_btn.png', False, True)
        close_btn_img = pg.transform.smoothscale(
            close_btn_img,
            (self._btn_width, self._btn_width))
        self.image.blit(
            close_btn_img,
            (title_bar_rect_abs.right - self._btn_width - self._btn_margin, self._btn_margin))

        self._inner_group.draw(self.image)

    def update(self, *args: Any, **kwargs: Any) -> None:
        super().update(*args, **kwargs)
        self._inner_group.update(*args, **kwargs)

    def calculate_size(self, max_width: int, max_height: int) -> tuple[int, int]:
        self.rect.width = max_width
        self.rect.height = max_height

        self._title_bar_rect = _calculate_title_bar_rect(self.rect, self._title_font)
        self._border_collide_rects = _calculate_border_collide_rects(
            self.rect if not self._is_minimized else self._title_bar_rect,
            RESIZE_RECT_TOLERANCE)

        self._btn_width = int(self._title_bar_rect.height * BUTTON_WIDTH_FACTOR)
        self._btn_margin = (self._title_bar_rect.height - self._btn_width) // 2

        self._minimize_btn_collide_rect = pg.Rect(
            self.rect.x + self._btn_margin,
            self.rect.y + self._btn_margin,
            self._btn_width,
            self._btn_width)

        self._close_btn_collide_rect = pg.Rect(
            self.rect.right - self._btn_margin - self._btn_width,
            self.rect.top + self._btn_margin,
            self._btn_width,
            self._btn_width)

        if not self._is_minimized:
            self._child_rect = _calculate_child_rect(self.rect, self._title_bar_rect)
            self.child.calculate_size(self._child_rect.width, self._child_rect.height)

        return (max_width, max_height)

    def set_placement(self, x: int, y: int) -> None:
        super().set_placement(x, y)

        self.child.set_placement(self._child_rect.x, self._child_rect.y)

def _calculate_title_bar_rect(base_rect: pg.Rect, title_font: pg.font.Font) -> pg.Rect:
    return pg.Rect(
        base_rect.x,
        base_rect.y,
        base_rect.width,
        title_font.get_height() + TITLE_OFFSET * 2)

def _calculate_child_rect(base_rect: pg.Rect, title_rect: pg.Rect) -> pg.Rect:
    # return pg.Rect(
    #     base_rect.left + BORDER_THICKNESS,
    #     base_rect.top + title_rect.height + BORDER_THICKNESS,
    #     base_rect.width - BORDER_THICKNESS * 2,
    #     base_rect.height - title_rect.height - BORDER_THICKNESS * 2)

    return pg.Rect(
        BORDER_THICKNESS,
        title_rect.height + BORDER_THICKNESS,
        base_rect.width - BORDER_THICKNESS * 2,
        base_rect.height - title_rect.height - BORDER_THICKNESS * 2)

def _calculate_border_collide_rects(base_rect: pg.Rect, tolerance: int) -> list[tuple[pg.Rect, Side]]:
    result = list[tuple[pg.Rect, Side]]()

    # left border
    rect = pg.Rect(
        base_rect.left - tolerance,
        base_rect.top - tolerance,
        tolerance * 2,
        base_rect.height + tolerance * 2)
    result.append((rect, Side.LEFT))

    # right border
    rect = pg.Rect(
        base_rect.right - tolerance,
        base_rect.top - tolerance,
        tolerance * 2,
        base_rect.height + tolerance * 2)
    result.append((rect, Side.RIGHT))

    # bottom border
    rect = pg.Rect(
        base_rect.left - tolerance,
        base_rect.bottom - tolerance,
        base_rect.width + tolerance * 2,
        tolerance * 2)
    result.append((rect, Side.BOTTOM))

    return result

# def _move_to_front(widget: Widget, group: pg.sprite.LayeredUpdates) -> None:
#     if isinstance(widget, ContainerWidget):
#         for child in widget.children:
#             group.move_to_front()

def _get_minimize_btn_img(is_minimized: bool, btn_width: int) -> pg.Surface:
    img: pg.Surface
    if is_minimized:
        img = _internal._ImageCache.try_get_image('./assets/window_minimize_btn_inactive.png', False, True)
    else:
        img = _internal._ImageCache.try_get_image('./assets/window_minimize_btn_active.png', False, True)

    return pg.transform.smoothscale(img, (btn_width, btn_width))
