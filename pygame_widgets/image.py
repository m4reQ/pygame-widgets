import enum
import typing as t
import uuid

import pygame as pg

from .widget import Widget


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
                  rounding: int = 0,
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
            rounding=rounding,
            _id=_id,
            rect=rect)

    def __init__(self,
                 img: pg.Surface,
                 *,
                 filter: ImageFilter = ImageFilter.LINEAR,
                 preserve_ratio: bool = False,
                 rounding: int = 0,
                 _id: uuid.UUID | None = None,
                 rect: pg.Rect | None = None) -> None:
        super().__init__(_id, rect)

        self._filter = filter
        self._preserve_aspect_ratio = preserve_ratio
        self._original_image = img
        self._rounding = rounding

        self.image = img

    def calculate_size(self, max_width: int, max_height: int) -> tuple[int, int]:
        super().calculate_size(max_width, max_height)

        if self._original_image.get_width() > max_width or self._original_image.get_height() > max_height:
            new_size: tuple[int, int]

            if self._preserve_aspect_ratio:
                new_size = _get_scale_aspect_ratio(self._original_image, max_width, max_height)
            else:
                new_size = _get_scale(self._original_image, max_width, max_height)

            if self._filter == ImageFilter.LINEAR:
                self.image = pg.transform.smoothscale(self._original_image, new_size)
            else:
                self.image = pg.transform.scale(self._original_image, new_size)

        if self._rounding != 0:
            dst_surf = pg.Surface(self.image.get_size(), pg.SRCALPHA)
            pg.draw.rect(
                dst_surf,
                (255, 255, 255, 255),
                pg.Rect(0, 0, self.image.get_width(), self.image.get_height()),
                border_radius=self._rounding)
            dst_surf.blit(self.image, (0, 0), special_flags=pg.BLEND_RGBA_MIN)

            self.image = dst_surf

        self.rect.size = self.image.get_size()
        return self.rect.size

def _get_scale_aspect_ratio(img: pg.Surface, width: int, height: int) -> tuple[int, int]:
    width_ratio = width / img.get_width()
    height_ratio = height / img.get_height()
    ratio = min(width_ratio, height_ratio)

    return (img.get_width() * ratio, img.get_height() * ratio)

def _get_scale(img: pg.Surface, width: int, height: int) -> tuple[int, int]:
    return (
        min(img.get_width(), width),
        min(img.get_height(), height))
