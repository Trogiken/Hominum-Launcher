"""
This module handles things related to the gui

Functions:
- get_settings() -> GUISettings: Get the settings from the settings file.
- save_settings(settings: GUISettings) -> pathlib.Path: Save the settings to the settings file.
- reset_settings() -> GUISettings: Reset the settings to the default values.

Classes:
- GUISettings: Stores the settings for the GUI.

Constants:
- SETTINGS_FILENAME: The name of the settings file.
- SETTINGS_PATH: The path to the settings file.
"""

import os
import pickle
import pathlib
from dataclasses import dataclass
from source.path import STORE_DIR


SETTINGS_FILENAME = "gui-settings.pkl"
SETTINGS_PATH = pathlib.Path(os.path.join(STORE_DIR, SETTINGS_FILENAME))


@dataclass
class GUISettings:
    """Stores the settings for the GUI."""
    font_type: str = "Arial"
    font_size_small: int = 10
    font_size_normal: int = 12
    font_size_large: int = 14
    font: tuple = (font_type, font_size_normal)
    font_small: tuple = (font_type, font_size_small)
    font_normal: tuple = (font_type, font_size_normal)
    font_large: tuple = (font_type, font_size_large)
    appearance: str = "system"


def reset_settings() -> GUISettings:
    """
    Reset the settings to the default values.

    Returns:
    - GUISettings: The default settings.
    """
    settings = GUISettings()
    save_settings(settings)
    return settings


def get_settings() -> GUISettings:
    """
    Get the settings from the settings file.

    Returns:
    - GUISettings: The settings.
    """
    if not os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, "wb") as f:
            pickle.dump(GUISettings(), f)
        return GUISettings()

    with open(SETTINGS_PATH, "rb") as f:
        return pickle.load(f)


def save_settings(settings: GUISettings) -> pathlib.Path:
    """
    Save the settings to the settings file.
    
    Parameters:
    - settings (GUISettings): The settings to save.
    
    Returns:
    - Path: The path to the settings file."""
    with open(SETTINGS_PATH, "wb") as f:
        pickle.dump(settings, f)
    return SETTINGS_PATH
