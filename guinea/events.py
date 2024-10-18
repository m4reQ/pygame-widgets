import typing as t
from collections import defaultdict

import pygame as pg

THandler = t.Callable[[pg.event.Event], None]

def process_event(event: pg.event.Event) -> None:
    for handler in _handlers[event.type]:
        handler(event)

def register_handler(event_type: int, handler: THandler) -> None:
    _handlers[event_type].add(handler)

def unregister_handler(handler: THandler) -> None:
    for _type in _handlers:
        _handlers[_type].remove(handler)

_handlers = defaultdict[int, set[THandler]](set)
