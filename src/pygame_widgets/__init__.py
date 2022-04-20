'''
A module for GUI creation in Pygame.
'''

from .text import Text, TextConfig, TextAlign
from .progress_bar import ProgressBar, ProgressBarConfig
from .button import Button, ButtonConfig, ButtonState

__all__ = [
    'Text',
    'TextConfig',
    'TextAlign',
    'ProgressBar',
    'ProgressBarConfig',
    'Button',
    'ButtonConfig',
    'ButtonState'
]


def init():
    '''
    Initializes pygame_widgets module.
    '''
