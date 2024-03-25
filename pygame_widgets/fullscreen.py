import uuid

import pygame as pg

from pygame_widgets.widget import ContainerWidget

from . import events
from .widget import SingleChildContainerWidget, Widget


class Fullscreen(SingleChildContainerWidget):
    def __init__(self,
                 child: Widget,
                 *,
                 _id: uuid.UUID | None = None) -> None:
        display_size = pg.display.get_surface().get_size()

        super().__init__(
            child,
            _id,
            pg.Rect((0, 0), display_size))

        events.register_handler(pg.VIDEORESIZE, self._handle_video_resize)

    def _handle_video_resize(self, event: pg.event.Event) -> None:
        self.rect.width = event.w
        self.rect.height = event.h

        self._needs_recalculate = True
        self._needs_reposition = True

    def set_parent(self, _: ContainerWidget) -> None:
        raise RuntimeError('Fullscreen widget can only be used as a top-level widget. It\'s parent cannot be set.')

    def calculate_size(self, max_width: int, max_height: int) -> tuple[int, int]:
        super().calculate_size(max_width, max_height)

        child_width, child_height = self.child.calculate_size(self.rect.width, self.rect.height)

        self.rect.width = child_width
        self.rect.height = child_height

        return (child_width, child_height)

    def set_placement(self, x: int, y: int) -> None:
        super().set_placement(x, y)

        self.child.set_placement(0, 0)
