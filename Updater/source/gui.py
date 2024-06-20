"""This module handles things related to the gui"""

from dataclasses import dataclass
from source.path import APPLICATION_PATH


@dataclass
class GUISettings:
    font_type: str = "Arial"
    font_size_small: int = 10
    font_size_normal: int = 12
    font_size_large: int = 14
    font: tuple = (font_type, font_size_normal)
    appearance: str = "system"


def get_settings():
    return GUISettings


def save_settings(settings: GUISettings):
    return None
