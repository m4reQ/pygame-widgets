from __future__ import annotations

import abc
import typing as t
import uuid

import pygame as pg


class Widget(pg.sprite.DirtySprite, abc.ABC):
    @staticmethod
    def generate_widget_id() -> uuid.UUID:
        return uuid.uuid4()

    @staticmethod
    def register_widget_stack(sprite_group: pg.sprite.AbstractGroup, stack: Widget) -> None:
        sprite_group.add(stack)

        if isinstance(stack, ContainerWidget):
            for child in stack.children:
                Widget.register_widget_stack(sprite_group, child)

    def __init__(self,
                 _id: uuid.UUID | None = None,
                 rect: pg.Rect | None = None) -> None:
        super().__init__()
        self._id = _id or Widget.generate_widget_id()

        self._constraints = (-1, -1) if rect is None else rect.size
        self.rect = pg.Rect(0, 0, 0, 0) if rect is None else rect

        self._needs_redraw = True
        self._needs_recalculate = True
        self._needs_reposition = True

        self.parent: ContainerWidget | None = None

    def set_parent(self, parent: ContainerWidget) -> None:
        self.parent = parent

    def calculate_size(self, max_width: int, max_height: int) -> tuple[int, int]:
        self._needs_recalculate = False

    def set_placement(self, x: int, y: int) -> None:
        self._needs_reposition = False

        self.rect.x = x
        self.rect.y = y

    def update(self, *args: t.Any, **kwargs: t.Any) -> None:
        super().update(*args, **kwargs)

        assert not (self.parent is None and self.rect is None), 'Cannot determine size and position of the widget, because parent and rect are not set'

        target_rect: pg.Rect
        if self.parent is not None:
            target_rect = self.parent.rect
        else:
            target_rect = self.rect

        if self._needs_recalculate:
            self.calculate_size(target_rect.width, target_rect.height)
            self._needs_redraw = True

        if self._needs_reposition:
            self.set_placement(target_rect.x, target_rect.y)
            self._needs_redraw = True

        if self._needs_redraw:
            self.redraw()

            self.dirty = 1

    def redraw(self) -> None:
        self._needs_redraw = False

    @property
    def id(self) -> uuid.UUID:
        return self._id

    @property
    def needs_redraw(self) -> bool:
        return self._needs_redraw

class ContainerWidget(Widget):
    def __init__(self,
                 children: list[Widget],
                 _id: uuid.UUID | None = None,
                 rect: pg.Rect | None = None) -> None:
        super().__init__(_id, rect)

        self._children = children
        for child in self._children:
            child.set_parent(self)

        self.visible = False
        self.dirty = 0

    # container widgets do not have to be redrawn
    def redraw(self) -> None:
        pass

    @property
    def children(self) -> list[Widget]:
        return self._children

class SingleChildContainerWidget(ContainerWidget):
    def __init__(self,
                 child: Widget,
                 _id: uuid.UUID | None = None,
                 rect: pg.Rect | None = None) -> None:
        super().__init__([child], _id, rect)

    @property
    def child(self) -> Widget:
        return self._children[0]
