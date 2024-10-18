import math
import os

import pygame as pg

from pygame_widgets.enums import OverflowBehavior
from pygame_widgets.shaders import Shader

TargetFill = pg.Color | pg.Surface | Shader

class _ImageCache:
    _cache: dict[tuple[str, bool], pg.Surface] = {}

    @staticmethod
    def try_get_image(filepath_or_url: str, is_from_url: bool, is_internal_asset: bool = False) -> pg.Surface:
        assert not (is_from_url and is_internal_asset), 'Internal asset cannot come from url'

        if is_internal_asset:
            filepath_or_url = os.path.join(os.path.dirname(__file__), filepath_or_url)

        key = (filepath_or_url, is_from_url)
        if key in _ImageCache._cache:
            return _ImageCache._cache[key]

        img: pg.Surface
        if is_from_url:
            raise NotImplementedError('Loading images from web is not supported yet.')
        else:
            img = pg.image.load(filepath_or_url)
            if img.get_bytesize() == 4:
                img = img.convert_alpha()
            else:
                img = img.convert()

        _ImageCache._cache[key] = img

        return img

class FontCache:
    _cache: dict[tuple[str, int], pg.font.Font] = {}

    @staticmethod
    def get_font(name: str, size: int) -> pg.font.Font:
        key = (name, size)
        if key in FontCache._cache:
            return FontCache._cache[key]

        font = pg.font.SysFont(name, size)
        FontCache._cache[key] = font

        return font

    @staticmethod
    def get_default_of_size(size: int) -> pg.font.Font:
        return FontCache.get_font('consolas', size)

def set_overflow_behavior(behavior: OverflowBehavior) -> None:
    global _overflow_behavior
    _overflow_behavior = behavior

def round(x: int | float) -> int:
    if _overflow_behavior == OverflowBehavior.OVERFLOW:
        return math.ceil(x)

    return math.floor(x)

def divide_with_overflow(x: int | float, y: int | float) -> int:
    return round(x / y)

def get_surface_flags_for_target_fill(fill: TargetFill) -> int:
    requires_alpha = any((
        isinstance(fill, pg.Color) and fill.a != 255,
        isinstance(fill, pg.Surface) and fill.get_alpha() is not None,
        isinstance(fill, Shader) and fill.requires_alpha()))
    return pg.SRCALPHA if requires_alpha else 0

def apply_target_fill_to_surface(surf: pg.Surface, fill: TargetFill, has_mask: bool) -> None:
    if isinstance(fill, pg.Color):
        surf.fill(fill)
    elif isinstance(fill, pg.Surface):
        pg.transform.smoothscale(fill, surf.get_size(), surf)
    else:
        fill.draw(surf, has_mask)

_overflow_behavior = OverflowBehavior.UNDERFLOW
