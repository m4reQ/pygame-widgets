import typing as t

import pygame as pg


def collide_point(point: t.Tuple[int, int],
                  rect: pg.Rect,
                  mask: t.Optional[pg.Mask] = None) -> bool:
    if not rect.collidepoint(point):
        return False

    if mask is None:
        return True

    return mask.get_at(
        (
            point[0] - rect.x,
            point[1] - rect.y)) != 0
