import abc
import typing as t

import pygame as pg

from pygame_widgets import internal


class WidgetBase(pg.sprite.DirtySprite, abc.ABC):
    def __init__(self,
                 event_handlers: list[tuple[int, internal._HandlerType]] = []) -> None: # noqa
        super().__init__()

        self.needs_redraw = False
        self.children: list[WidgetBase] = []

        self._register_event_handlers(event_handlers)

    def redraw(self) -> None:
        pass

    def _register_event_handlers(self,
                                 handlers: list[tuple[int, internal._HandlerType]]) -> None: # noqa
        for _type, handler in handlers:
            internal.add_event_handler(_type, handler)


_StateType = t.TypeVar('_StateType')


class StateHandle(t.Generic[_StateType], abc.ABC):
    _state: _StateType | None = None
    _state_changed: bool = False

    @property
    def state(self) -> _StateType:
        if self._state is None:
            raise RuntimeError('State has to be initialized when calling state.__get__.') # noqa

        return self._state

    @state.setter
    def state(self, value: _StateType) -> None:
        if value != self._state:
            self._state_changed = True

        self._state = value

    @property
    def state_changed(self) -> bool:
        value = self._state_changed
        self._state_changed = False

        return value
