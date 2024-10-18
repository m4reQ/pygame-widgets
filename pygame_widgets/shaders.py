import abc
import typing as t

import pygame as pg

from pygame_widgets.enums import Direction


class Shader(abc.ABC):
    @abc.abstractmethod
    def draw(self, img: pg.Surface, has_mask: bool) -> None:
        pass

    @abc.abstractmethod
    def requires_alpha(self) -> bool:
        pass

class GradientShader(Shader):
    def __init__(self, stops: list[pg.Color], direction: Direction) -> None:
        self.stops = stops
        self.direction = direction

    def draw(self, img: pg.Surface, has_mask: bool) -> None:
        width: int
        height: int
        if self.direction == Direction.LEFT or self.direction == Direction.RIGHT:
            width = len(self.stops)
            height = 2
        else:
            width = 2
            height = len(self.stops)

        result = pg.Surface((width, height))

        stops_iter: t.Iterator[pg.Color]
        if self.direction == Direction.LEFT or self.direction == Direction.UP:
            stops_iter = reversed(self.stops)
        else:
            stops_iter = iter(self.stops)

        if self.direction == Direction.UP or self.direction == Direction.DOWN:
            for i, color in enumerate(stops_iter):
                pg.draw.line(result, color, (0, i), (1, i))
        else:
            for i, color in enumerate(stops_iter):
                pg.draw.line(result, color, (i, 0), (i, 1))

        result = pg.transform.smoothscale(result, img.get_size())
        img.blit(result, (0, 0), special_flags=pg.BLEND_RGBA_MIN if has_mask else 0)

    def requires_alpha(self) -> bool:
        return any(color.a != 255 for color in self.stops)
