"""
This module handles things related to the gui

Functions:
- get_settings() -> GUISettings: Get the settings from the settings file.
- save_settings(settings: GUISettings) -> pathlib.Path: Save the settings to the settings file.
- reset_settings() -> GUISettings: Reset the settings to the default values.
- get_image(image_name: str) -> Image: Get the image from the assets directory.

Classes:
- Settings: Stores the settings for the program.

Constants:
- SETTINGS_FILENAME: The name of the settings file.
- SETTINGS_PATH: The path to the settings file.
"""

import os
import pickle
import pathlib
from dataclasses import dataclass, field
from PIL import Image
from source import path


SETTINGS_FILENAME = "settings.pkl"
SETTINGS_PATH = pathlib.Path(os.path.join(path.STORE_DIR, SETTINGS_FILENAME))


@dataclass
class GUISettings:
    """Stores the settings for the GUI."""
    font_small: tuple = ("Helvetica", 12)
    font_normal: tuple = ("Helvetica", 14)
    font_large: tuple = ("Helvetica", 16)
    appearance: str = "system"
    image_small: tuple = (14, 14)
    image_normal: tuple = (18, 18)
    image_large: tuple = (24, 24)


@dataclass
class UserSettings:
    """Stores the settings for the user."""
    email: str = ""
    cache_session: bool = True
    # TODO: Add whitelist mods here also


@dataclass
class GameSettings:
    """Stores the settings for the game."""
    jvm_args: list = field(default_factory=lambda: [
        "-Xmx2G",
        "-XX:+UnlockExperimentalVMOptions",
        "-XX:+UseG1GC",
        "-XX:G1NewSizePercent=20",
        "-XX:G1ReservePercent=20",
        "-XX:MaxGCPauseMillis=50",
        "-XX:G1HeapRegionSize=32M"
    ])


# TODO: Fix docstring format
class Settings:
    """
    A class that represents the settings for the application.

    Methods:
    - load: Reads the settings from a file.
    - save: Writes the settings to a file.
    - reset: Reset the settings to the default values.
    - get_gui: Retrieves a specific GUI setting.
    - get_user: Retrieves a specific user setting.
    - get_game: Retrieves a specific game setting.
    - set_gui: Updates the GUI settings.
    - set_user: Updates the user settings.
    - set_game: Updates the game settings.
    """

    def __init__(self):
        self._gui = None
        self._user = None
        self._game = None
        self.load()

    def load(self):
        """
        Reads the settings from a file.
        If the file doesn't exist, default settings are used.
        """
        try:
            with open(SETTINGS_PATH, 'rb') as f:
                data = pickle.load(f)
                self._gui = data.get('gui', GUISettings())
                self._user = data.get('user', UserSettings())
                self._game = data.get('game', GameSettings())
        except FileNotFoundError:
            self._gui = GUISettings()
            self._user = UserSettings()
            self._game = GameSettings()
            self.save()

    def save(self):
        """
        Writes the settings to a file.
        """
        data = {
            'gui': self._gui,
            'user': self._user,
            'game': self._game,
        }
        with open(SETTINGS_PATH, 'wb') as f:
            pickle.dump(data, f)
        self.load()

    def reset(self):
        """
        Reset the settings to the default values.
        """
        self._gui = GUISettings()
        self._user = UserSettings()
        self._game = GameSettings()
        self.save()

    def get_gui(self, key: str) -> any:
        """
        Retrieves a specific GUI setting.

        Parameters:
        - key (str): The key of the setting to retrieve.

        Returns:
        - Any: The value of the setting.
        """
        self.load()
        return getattr(self._gui, key)

    def get_user(self, key: str) -> any:
        """
        Retrieves a specific user setting.

        Parameters:
        - key (str): The key of the setting to retrieve.

        Returns:
        - Any: The value of the setting.
        """
        self.load()
        return getattr(self._user, key)

    def get_game(self, key: str) -> any:
        """
        Retrieves a specific game setting.

        Parameters:
        - key (str): The key of the setting to retrieve.

        Returns:
        - Any: The value of the setting.
        """
        self.load()
        return getattr(self._game, key)

    def set_gui(self, **kwargs) -> None:
        """
        Updates the GUI settings.

        Parameters:
        - **kwargs: Keyword arguments representing the settings to update.
        """
        for key, value in kwargs.items():
            setattr(self._gui, key, value)
        self.save()

    def set_user(self, **kwargs) -> None:
        """
        Updates the user settings.

        Parameters:
        - **kwargs: Keyword arguments representing the settings to update.
        """
        for key, value in kwargs.items():
            setattr(self._user, key, value)
        self.save()

    def set_game(self, **kwargs) -> None:
        """
        Updates the game settings.

        Parameters:
        - **kwargs: Keyword arguments representing the settings to update.
        """
        for key, value in kwargs.items():
            setattr(self._game, key, value)
        self.save()


def get_image(image_name: str) -> Image.Image:
    """
    Get the image from the assets directory.

    Parameters:
    - image_name (str): The name of the image.

    Returns:
    - Image: The image.
    """
    return Image.open(path.ASSETS_DIR / "images" / image_name)
