import abc
import typing as t

import pygame as pg


class WidgetBase(pg.sprite.DirtySprite, abc.ABC):
    def __init__(self) -> None:
        super().__init__()

        self.needs_redraw = False
        self.children: list[WidgetBase] = []

    def update(self, *args: t.Any, **kwargs: t.Any) -> None:
        super().update(*args, **kwargs)

        if not self.needs_redraw:
            return

        self.redraw()

        self.dirty = 1
        self.needs_redraw = False

    def redraw(self) -> None:
        pass
