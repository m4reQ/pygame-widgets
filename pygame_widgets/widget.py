from __future__ import annotations

import abc
import typing as t
import uuid

import pygame as pg

from pygame_widgets import _internal
from pygame_widgets.enums import MainAxisSize


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

    @property
    def children_count(self) -> int:
        return len(self._children)

class AxialContainer(ContainerWidget):
    def __init__(self,
                 children: list[Widget],
                 spacing: int,
                 axis: bool,
                 main_axis_size: MainAxisSize,
                 _id: uuid.UUID | None = None,
                 rect: pg.Rect | None = None) -> None:
        super().__init__(children, _id, rect)

        self._axis = axis
        self._spacing = spacing
        self._max_child_space = 0
        self._main_axis_size = main_axis_size

    def _calculate_available_space(self, max_width: int, max_height: int) -> int:
        return (max_height if self._axis else max_width) - self._spacing * (self.children_count - 1)

    def _space_children_evenly(self, max_width: int, max_height: int) -> tuple[int, int]:
        available_space = self._calculate_available_space(max_width, max_height)
        self._max_child_space = _internal.divide_with_overflow(available_space, self.children_count)

        width_used = height_used = 0
        for child in self._children:
            if self._axis:
                child_width, _ = child.calculate_size(max_width, self._max_child_space)

                width_used = max(width_used, child_width)
                height_used += self._max_child_space + self._spacing
            else:
                _, child_height = child.calculate_size(self._max_child_space, max_height)

                width_used += self._max_child_space + self._spacing
                height_used = max(height_used, child_height)

        return (width_used, height_used)

    def _space_children_min_size(self, max_width: int, max_height: int) -> tuple[int, int]:
        available_space = self._calculate_available_space(max_width, max_height)
        self._max_child_space = _internal.divide_with_overflow(available_space, self.children_count)

        width_used = height_used = 0
        for child in self._children:
            if self._axis:
                child_width, child_height = child.calculate_size(max_width, available_space)
                child_height += self._spacing

                height_used += child_height
                width_used = max(width_used, child_width)

                available_space -= child_height
            else:
                child_width, child_height = child.calculate_size(available_space, max_height)
                child_width += self._spacing

                height_used = max(height_used, child_height)
                width_used += child_width

                available_space -= child_width

        return (width_used, height_used)

    def calculate_size(self, max_width: int, max_height: int) -> tuple[int, int]:
        super().calculate_size(max_width, max_height)

        if self._main_axis_size == MainAxisSize.EVEN:
            self.rect.size = self._space_children_evenly(max_width, max_height)
        else:
            self.rect.size = self._space_children_min_size(max_width, max_height)

        return self.rect.size

    def set_placement(self, x: int, y: int) -> None:
        super().set_placement(x, y)

        offset = 0
        for child in self._children:
            if self._axis:
                child.set_placement(x, y + offset)
            else:
                child.set_placement(x + offset, y)

            offset_increment: int
            if self._main_axis_size == MainAxisSize.EVEN:
                offset_increment = self._max_child_space
            else:
                offset_increment = child.rect.height if self._axis else child.rect.width

            offset += offset_increment + self._spacing

class SingleChildContainerWidget(ContainerWidget):
    def __init__(self,
                 child: Widget,
                 _id: uuid.UUID | None = None,
                 rect: pg.Rect | None = None) -> None:
        super().__init__([child], _id, rect)

    @property
    def child(self) -> Widget:
        return self._children[0]
