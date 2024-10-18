from __future__ import annotations

import typing as t
import uuid

import pygame as pg

from . import events
from .widget import SingleChildContainerWidget, Widget


class Button(SingleChildContainerWidget):
    def __init__(self,
                 child: Widget,
                 *,
                 on_hover: t.Callable[[Button, bool], None] | None = None,
                 on_click: t.Callable[[Button, pg.event.Event], None] | None = None,
                 use_mask: bool = True,
                 _id: uuid.UUID | None = None,
                 rect: pg.Rect | None = None) -> None:
        super().__init__(child, _id, rect)

        self._on_hover = on_hover
        self._on_click = on_click
        self._last_hovered = False
        self._use_mask = use_mask

        events.register_handler(pg.MOUSEBUTTONDOWN, self._click_handler)
        events.register_handler(pg.MOUSEMOTION, self._mouse_motion_handler)

    def _mouse_motion_handler(self, event: pg.event.Event) -> None:
        mouse_inside = self.rect.collidepoint(event.pos)

        if self._on_hover is not None:
            if mouse_inside and not self._last_hovered and self._on_hover is not None:
                self._on_hover(self, True)
            elif not mouse_inside and self._last_hovered:
                self._on_hover(self, False)

        self._last_hovered = mouse_inside

    def _click_handler(self, event: pg.event.Event) -> None:
        collided = self.rect.collidepoint(event.pos)

        if collided and self._on_click is not None:
            self._on_click(self, event)

    def calculate_size(self, max_width: int, max_height: int) -> tuple[int, int]:
        super().calculate_size(max_width, max_height)

        self.rect.width, self.rect.height = self.child.calculate_size(max_width, max_height)

        return self.rect.size

    def set_placement(self, x: int, y: int) -> None:
        super().set_placement(x, y)

        self.child.set_placement(x, y)
