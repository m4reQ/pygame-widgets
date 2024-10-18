import typing as t
import uuid

import pygame as pg

from guinea import _internal
from guinea._internal import TargetFill
from guinea.enums import HAlignment, VAlignment
from guinea.widget import ContainerWidget, Widget


class PaddingValue:
    @t.overload
    def __init__(self, x: int) -> None: ...

    @t.overload
    def __init__(self, horizontal: int, vertical: int) -> None: ...

    @t.overload
    def __init__(self, left: int, right: int, top: int, bottom: int) -> None: ...

    # mypy bug
    def __init__(self, *args: int) -> None: # type: ignore[misc]
        if len(args) == 1:
            self.left = args[0]
            self.right = args[0]
            self.top = args[0]
            self.bottom = args[0]
        elif len(args) == 2:
            self.left = self.right = args[0]
            self.top = self.bottom = args[1]
        elif len(args) == 4:
            self.left = args[0]
            self.right = args[1]
            self.top = args[2]
            self.bottom = args[3]
        else:
            raise ValueError('Invalid padding arguments.')

    @property
    def axis_x(self) -> int:
        return self.left + self.right

    @property
    def axis_y(self) -> int:
        return self.top + self.bottom


class Container(ContainerWidget):
    def __init__(self,
                 child: Widget | None = None,
                 *,
                 bg: TargetFill | None = None,
                 rounding: int = -1,
                 v_expand: bool = False,
                 h_expand: bool = False,
                 v_alignment: VAlignment = VAlignment.TOP,
                 h_alignment: HAlignment = HAlignment.LEFT,
                 padding: PaddingValue | None = None,
                 _id: uuid.UUID | None = None,
                 rect: pg.Rect | None = None) -> None:
        super().__init__([] if child is None else [child], _id, rect)

        self.bg = bg
        self.rounding = rounding
        self.v_expand = v_expand
        self.h_expand = h_expand
        self.v_alignment = v_alignment
        self.h_alignment = h_alignment
        self.padding = padding or PaddingValue(0)

        self.visible = bg is not None

        self.image = pg.Surface((0, 0))

    @property
    def child(self) -> Widget | None:
        return None if len(self.children) == 0 else self.children[0]

    def set_bg(self, bg: TargetFill) -> None:
        self.bg = bg
        self._needs_redraw = True

    def set_fg(self, fg: TargetFill) -> None:
        self.fg = fg
        self._needs_redraw = True

    def set_placement(self, x: int, y: int) -> None:
        super().set_placement(x, y)

        if self.child is None:
            return

        child_rect = self.child.rect

        if self.v_expand:
            if self.v_alignment == VAlignment.CENTER:
                y += _internal.divide_with_overflow(self.rect.height - self.padding.axis_y, 2) - _internal.divide_with_overflow(child_rect.height, 2)
            elif self.v_alignment == VAlignment.BOTTOM:
                y += self.rect.height - self.padding.bottom - child_rect.height - self.padding.top

        if self.h_expand:
            if self.h_alignment == HAlignment.CENTER:
                x += _internal.divide_with_overflow(self.rect.width - self.padding.axis_x, 2) - _internal.divide_with_overflow(child_rect.width, 2)
            elif self.h_alignment == HAlignment.RIGHT:
                x += self.rect.width - self.padding.right - child_rect.width - self.padding.left

        self.child.set_placement(x + self.padding.left, y + self.padding.top)

    def calculate_size(self, max_width: int, max_height: int) -> tuple[int, int]:
        super().calculate_size(max_width, max_height)

        own_width = max_width
        own_height = max_height
        if self.child is None:
            if not self.v_expand:
                own_height = 0

            if not self.h_expand:
                own_width = 0
        else:
            child_width, child_height = self.child.calculate_size(
                max_width - self.padding.axis_x,
                max_height - self.padding.axis_y)

            if not self.v_expand:
                own_height = child_height

            if not self.h_expand:
                own_width = child_width

        self.rect.width = own_width
        self.rect.height = own_height

        return self.rect.size

    def redraw(self) -> None:
        if self.bg is None:
            self.image = pg.Surface((0, 0))
            return

        is_rounded = self.rounding != -1

        surface_flags = _internal.get_surface_flags_for_target_fill(self.bg) | (pg.SRCALPHA if is_rounded else 0)
        self.image = pg.Surface(
            self.rect.size,
            surface_flags)

        if isinstance(self.bg, pg.Color):
            pg.draw.rect(self.image, self.bg, self.image.get_rect(), border_radius=self.rounding)
        elif isinstance(self.bg, pg.Surface):
            if self.rounding == -1:
                pg.transform.smoothscale(
                    self.bg,
                    self.image.get_size(),
                    self.image)
            else:
                pg.draw.rect(
                    self.image,
                    (255, 255, 255, 255),
                    self.image.get_rect(),
                    border_radius=self.rounding)
                self.image.blit(
                    pg.transform.smoothscale(self.bg, self.image.get_size()),
                    (0, 0),
                    special_flags=pg.BLEND_RGBA_MIN)
        else: # isinstance(self.bg, Shader)
            if is_rounded:
                pg.draw.rect(
                    self.image,
                    (255, 255, 255, 255),
                    self.image.get_rect(),
                    border_radius=self.rounding)
            self.bg.draw(self.image, is_rounded)
