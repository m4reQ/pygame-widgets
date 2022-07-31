import dataclasses
import enum
import typing as t

import pygame as pg

from pygame_widgets.internal import ConfigBase, WidgetBase


class ListOrient(enum.Enum):
    VERTICAL = enum.auto()
    HORIZONTAL = enum.auto()


@dataclasses.dataclass
class ListViewConfig(ConfigBase):
    # TODO: validate these two fields basing on orient # noqa
    item_width: int = 0
    item_height: int = 0
    bg_color: pg.Color = pg.Color(255, 255, 255, 255)
    orient: ListOrient = ListOrient.VERTICAL
    item_spacing: int = 0


_ItemType = t.TypeVar('_ItemType')
_ListItemFactoryType = t.Callable[[pg.Rect, int, _ItemType], WidgetBase]


class ListView(WidgetBase, t.Generic[_ItemType]):
    def __init__(self,
                 rect: pg.Rect,
                 items: t.List[_ItemType],
                 list_item_factory: _ListItemFactoryType[_ItemType],
                 config: ListViewConfig = ListViewConfig()) -> None:
        super().__init__()

        self.config = config
        self.rect: pg.Rect = rect
        self.image = self._render_bg_image()

        self._item_factory = list_item_factory
        self._items = items
        self._current_offset = 0

        self._render_image()

    def _render_bg_image(self) -> pg.Surface:
        config = self.config

        img = pg.Surface(
            self.rect.size,
            pg.SRCALPHA if config.bg_color.a != 255 else 0)
        img.fill(config.bg_color)

        return img

    def _render_image(self) -> None:
        for i, item in enumerate(self._items):
            pos: t.Tuple[int, int]
            if self.config.orient == ListOrient.HORIZONTAL:
                pos = (
                    self.rect.left + self._current_offset,
                    self.rect.top)
                self._current_offset += self.config.item_width
            else:
                pos = (
                    self.rect.left,
                    self.rect.top + self._current_offset)
                self._current_offset += self.config.item_height

            rect = pg.Rect(*pos, *self.rect.size)
            widget = self._item_factory(rect, i, item)

            self.children.append(widget)
