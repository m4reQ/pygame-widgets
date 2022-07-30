'''
A module for GUI creation in Pygame.
'''

from .button import Button, ButtonConfig
from .internal import update
from .list_view import ListView, ListViewConfig
from .progress_bar import ProgressBar, ProgressBarConfig
from .text import Text, TextAlign, TextConfig

__all__ = [
    'Text',
    'TextConfig',
    'TextAlign',
    'ProgressBar',
    'ProgressBarConfig',
    'Button',
    'ButtonConfig',
    'ListViewConfig',
    'ListView',
    'update'
]


def init():
    '''
    Initializes pygame_widgets module.
    '''
