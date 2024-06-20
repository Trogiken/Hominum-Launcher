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
from PIL import Image
from source import path


SETTINGS_FILENAME = "gui-settings.pkl"
SETTINGS_PATH = pathlib.Path(os.path.join(path.STORE_DIR, SETTINGS_FILENAME))


@dataclass
class GUISettings:
    """Stores the settings for the GUI."""
    font_type: str = "Helvetica"
    font_size_small: int = 12
    font_size_normal: int = 14
    font_size_large: int = 16
    font: tuple = (font_type, font_size_normal)
    font_small: tuple = (font_type, font_size_small)
    font_normal: tuple = (font_type, font_size_normal)
    font_large: tuple = (font_type, font_size_large)
    appearance: str = "system"
    image_small: tuple = (14, 14)
    image_normal: tuple = (18, 18)
    image_large: tuple = (24, 24)


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


def get_image(image_name: str) -> Image.Image:
    """
    Get the image from the assets directory.

    Parameters:
    - image_name (str): The name of the image.

    Returns:
    - Image: The image.
    """
    return Image.open(path.ASSETS_DIR / "images" / image_name)
