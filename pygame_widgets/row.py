import typing as t
import uuid

import pygame as pg

from pygame_widgets.enums import MainAxisSize
from pygame_widgets.widget import AxialContainer, Widget

TElement = t.TypeVar('TElement')

class Row(AxialContainer):
    @classmethod
    def build(cls,
              values: t.Iterable[TElement],
              factory: t.Callable[[int, TElement], Widget],
              *,
              spacing: int = 0,
              main_axis_size: MainAxisSize = MainAxisSize.MIN,
              _id: uuid.UUID | None = None,
              rect: pg.Rect | None = None) -> None:
        return cls(
            [factory(i, x) for i, x in enumerate(values)],
            spacing=spacing,
            main_axis_size=main_axis_size,
            _id=_id,
            rect=rect)

    def __init__(self,
                 children: list[Widget],
                 *,
                 spacing: int = 0,
                 main_axis_size: MainAxisSize = MainAxisSize.MIN,
                 _id: uuid.UUID | None = None,
                 rect: pg.Rect | None = None) -> None:
        super().__init__(children, spacing, False, main_axis_size, _id, rect)
