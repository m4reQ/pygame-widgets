import enum
import typing as t
import uuid

import pygame as pg

from .widget import ContainerWidget, Widget


class ImageFilter(enum.Enum):
    NEAREST = enum.auto()
    LINEAR = enum.auto()

class Image(Widget):
    @classmethod
    def from_file(cls,
                  filepath: str,
                  *,
                  filter: ImageFilter = ImageFilter.LINEAR,
                  preserve_ratio: bool = False,
                  _id: uuid.UUID | None = None,
                  rect: pg.Rect | None = None) -> t.Self:
        img = pg.image.load(filepath)

        if img.get_bytesize() == 4:
            img = img.convert_alpha()
        else:
            img = img.convert()

        return cls(
            img,
            filter=filter,
            preserve_ratio=preserve_ratio,
            _id=_id,
            rect=rect)

    def __init__(self,
                 img: pg.Surface,
                 *,
                 filter: ImageFilter = ImageFilter.LINEAR,
                 preserve_ratio: bool = False,
                 _id: uuid.UUID | None = None,
                 rect: pg.Rect | None = None) -> None:
        super().__init__(_id, rect)

        self.image = img
        self._filter = filter
        self._preserve_aspect_ratio = preserve_ratio

    def _get_scale_aspect_ratio(self, width: int, height: int) -> tuple[int, int]:
        width_ratio = width / self.image.get_width()
        height_ratio = height / self.image.get_height()
        ratio = min(width_ratio, height_ratio)

        return (self.image.get_width() * ratio, self.image.get_height() * ratio)

    def _get_scale(self, width: int, height: int) -> tuple[int, int]:
        return (
            min(self.image.get_width(), width),
            min(self.image.get_height(), height))

    def calculate_size(self, max_width: int, max_height: int) -> tuple[int, int]:
        super().calculate_size(max_width, max_height)

        if self.image.get_width() > max_width or self.image.get_height() > max_height:
            new_size: tuple[int, int]

            if self._preserve_aspect_ratio:
                new_size = self._get_scale_aspect_ratio(max_width, max_height)
            else:
                new_size = self._get_scale(max_width, max_height)

            if self._filter == ImageFilter.LINEAR:
                self.image = pg.transform.smoothscale(self.image, new_size)
            else:
                self.image = pg.transform.scale(self.image, new_size)

        self.rect.size = self.image.get_size()
        return self.rect.size
