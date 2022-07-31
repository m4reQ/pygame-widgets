from __future__ import annotations

import abc
import dataclasses
import queue
import time
import typing as t
from collections import defaultdict

import pygame as pg

_HandlerType = t.Callable[[pg.event.Event], t.Any]
_StateType = t.TypeVar('_StateType')


@dataclasses.dataclass
class ConfigBase(abc.ABC):
    def merge(self, other):
        '''
        Merges two configurations, updating or adding all
        non-default values from the provided instance.
        '''

        if not isinstance(other, self.__class__):
            raise TypeError('Can only concatenate two configurations of the same type.') # noqa

        for attr_name in vars(other):
            val = getattr(other, attr_name)
            default_value = getattr(self.__class__, attr_name)
            if val != default_value:
                setattr(self, attr_name, val)

        return self


class WidgetBase(pg.sprite.DirtySprite, abc.ABC):
    def __init__(self,
                 event_handlers: t.List[t.Tuple[int, _HandlerType]] = []) -> None: # noqa
        super().__init__()

        self.needs_redraw = False
        self.children: t.List[WidgetBase] = []

        self._register_event_handlers(event_handlers)

    def redraw(self) -> None:
        pass

    def _register_event_handlers(self,
                                 handlers: t.List[t.Tuple[int, _HandlerType]]) -> None: # noqa
        for _type, handler in handlers:
            add_event_handler(_type, handler)


class StateHandle(t.Generic[_StateType], abc.ABC):
    _state: t.Optional[_StateType] = None
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


def add_event_handler(event_type: int, handler: _HandlerType) -> None:
    if handler in _event_handlers[event_type]:
        return

    _event_handlers[event_type].append(handler)


def schedule_call(func: t.Callable[[], t.Any]) -> None:
    _scheduled_calls.put_nowait(func)


def call_after(func: t.Callable[[], t.Any], seconds: float) -> None:
    _after_calls.append((func, time.perf_counter(), seconds))


def update(events: t.Optional[t.Iterable[pg.event.Event]]) -> t.Dict[str, float]: # noqa
    '''
    Internally processes all events allowing widgets to response to user input.
    NOTE:
    If events argument is `None` this function will not invoke
    internal event handlers effectively halting all events.
    This behavior is designed to allow user to use `internal._invoke_event`
    withing the main game loop. This will reduce overhead that comes
    from iterating over the list of events multiple times.
    Keep in mind that functions like `internal._invoke_event`
    are not part of public API and you should use them only if
    you know what you are doing.

    @events: List of current frame events.
    '''

    times: t.Dict[str, float] = {}

    if events is None:
        times['events'] = 0.0
    else:
        start = time.perf_counter()
        for event in events:
            _invoke_event(event)

        times['events'] = time.perf_counter() - start

    start = time.perf_counter()
    while not _scheduled_calls.empty():
        _scheduled_calls.get_nowait()()

    for entry in _after_calls:
        cur = time.perf_counter()
        if entry[1] + entry[2] >= cur:
            entry[0]()
            _after_calls.remove(entry)
    times['scheduled_calls'] = time.perf_counter() - start

    return times


def _invoke_event(event: pg.event.Event) -> None:
    for handler in _event_handlers[event.type]:
        handler(event)


_event_handlers: t.DefaultDict[int, t.List[_HandlerType]] = defaultdict(list)
_scheduled_calls = queue.Queue[t.Callable[[], t.Any]]()
_after_calls: t.List[t.Tuple[t.Callable[[], t.Any], float, float]] = []
