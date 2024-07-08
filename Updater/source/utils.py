"""
This module handles things related to the gui

Functions:
- get_image: Get the image from the assets directory.
- get_html_resp: Get the HTML response from the assets directory.
- open_directory: Open a folder on the users computer.

Classes:
- GUISettings: Stores the settings for the GUI.
- UserSettings: Stores the settings for the user.
- GameSettings: Stores the settings for the game.
- Settings: Stores the settings for the program.


Constants:
- SETTINGS_FILENAME: The name of the settings file.
- SETTINGS_PATH: The path to the settings file.
"""

import logging
import os
import subprocess
import platform
import pickle
import pathlib
from dataclasses import dataclass, field
from PIL import Image
from source import path

logger = logging.getLogger(__name__)

SETTINGS_FILENAME = "settings.pkl"
SETTINGS_PATH = pathlib.Path(os.path.join(path.STORE_DIR, SETTINGS_FILENAME))


@dataclass
class GUISettings:
    """Stores the settings for the GUI."""
    main_window_geometry: tuple = (1200, 500)
    main_window_min_size: tuple = (1000, 400)
    font_small: tuple = ("Helvetica", 12)
    font_normal: tuple = ("Helvetica", 14)
    font_large: tuple = ("Helvetica", 16)
    font_title: tuple = ("Helvetica", 16, "bold")
    appearance: str = "system"
    image_small: tuple = (14, 14)
    image_normal: tuple = (18, 18)
    image_large: tuple = (24, 24)


@dataclass
class UserSettings:
    """Stores the settings for the user."""
    email: str = ""


@dataclass
class GameSettings:
    """Stores the settings for the game."""
    first_start: bool = True
    autojoin: bool = True
    ram_jvm_args: list = field(default_factory=lambda: ["-Xms2048M", "-Xmx2048M"])
    additional_jvm_args: list = field(default_factory=lambda: [
        "-XX:+UnlockExperimentalVMOptions",
        "-XX:+UseG1GC",
        "-XX:G1NewSizePercent=20",
        "-XX:G1ReservePercent=20",
        "-XX:MaxGCPauseMillis=50",
        "-XX:G1HeapRegionSize=32M"
    ])


class Settings:
    """
    A class that represents the settings for the application.

    Methods:
    - load: Reads the settings from a file.
    - save: Writes the settings to a file.
    - reset: Reset the settings to the default values.
    - reset_gui: Reset the GUI settings to the default values.
    - reset_user: Reset the user settings to the default values.
    - reset_game: Reset the game settings to the default values.
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
            logger.warning("Settings file not found. Default settings used.")

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
        logger.debug("Settings reset to default values.")

    def reset_gui(self):
        """
        Reset the GUI settings to the default values.
        """
        self._gui = GUISettings()
        self.save()
        logger.info("GUI settings reset to default values.")

    def reset_user(self):
        """
        Reset the user settings to the default values.
        """
        self._user = UserSettings()
        self.save()
        logger.info("User settings reset to default values.")

    def reset_game(self):
        """
        Reset the game settings to the default values.
        """
        self._game = GameSettings()
        self.save()
        logger.info("Game settings reset to default values.")

    def get_gui(self, key: str) -> any:
        """
        Retrieves a specific GUI setting.

        Parameters:
        - key (str): The key of the setting to retrieve.

        Returns:
        - Any: The value of the setting.
        """
        self.load()
        value = getattr(self._gui, key)
        logger.debug("GUI setting '%s' retrieved value '%s'", key, value)
        return value

    def get_user(self, key: str) -> any:
        """
        Retrieves a specific user setting.

        Parameters:
        - key (str): The key of the setting to retrieve.

        Returns:
        - Any: The value of the setting.
        """
        self.load()
        value = getattr(self._user, key)
        logger.debug("User setting '%s' retrieved value '%s'", key, value)
        return value

    def get_game(self, key: str) -> any:
        """
        Retrieves a specific game setting.

        Parameters:
        - key (str): The key of the setting to retrieve.

        Returns:
        - Any: The value of the setting.
        """
        self.load()
        value = getattr(self._game, key)
        logger.debug("Game setting '%s' retrieved value '%s'", key, value)
        return value

    def set_gui(self, **kwargs) -> None:
        """
        Updates the GUI settings.

        Parameters:
        - **kwargs: Keyword arguments representing the settings to update.
        """
        for key, value in kwargs.items():
            setattr(self._gui, key, value)
            logger.debug("GUI setting '%s' updated to value '%s'", key, value)
        self.save()

    def set_user(self, **kwargs) -> None:
        """
        Updates the user settings.

        Parameters:
        - **kwargs: Keyword arguments representing the settings to update.
        """
        for key, value in kwargs.items():
            setattr(self._user, key, value)
            logger.debug("User setting '%s' updated to value '%s'", key, value)
        self.save()

    def set_game(self, **kwargs) -> None:
        """
        Updates the game settings.

        Parameters:
        - **kwargs: Keyword arguments representing the settings to update.
        """
        for key, value in kwargs.items():
            setattr(self._game, key, value)
            logger.debug("Game setting '%s' updated to value '%s'", key, value)
        self.save()


def get_image(image_name: str) -> Image.Image:
    """
    Get the image from the assets directory.

    Parameters:
    - image_name (str): The name of the image.

    Returns:
    - Image: The image.
    """
    try:
        image = Image.open(path.ASSETS_DIR / "images" / image_name)
    except FileNotFoundError:
        logger.error("Image '%s' not found", image_name)
        raise
    logger.debug("Image '%s' loaded", image_name)
    return image


def get_html_resp() -> str:
    """
    Get the HTML response from the assets directory.

    Exceptions:
    - FileNotFoundError: If the HTML response is not found.

    Returns:
    - str: The HTML response.
    """
    try:
        with open(path.ASSETS_DIR / "resp.html", "r", encoding="utf-8") as f:
            html_resp = f.read()
    except FileNotFoundError:
        logger.error("HTML response not found")
        raise
    logger.debug("HTML response loaded")
    return html_resp


def open_directory(directory_path: str | pathlib.Path):
    """
    Open a folder on the users computer.

    Parameters:
    - directory_path (str | pathlib.Path): The directory to open.
    """
    system_platform = platform.system()

    if system_platform == "Windows":
        os.startfile(directory_path)  # pylint: disable=no-member
    elif system_platform == "Darwin":  # macOS
        with subprocess.Popen(["open", directory_path]) as proc:
            proc.communicate()
    else:  # Linux and other Unix-like systems
        with subprocess.Popen(["xdg-open", directory_path]) as proc:
            proc.communicate()
    logger.debug("Opened directory: '%s'", directory_path)


def format_number(n: float) -> str:
    """
    Format a float into correct measurement

    Returns:
    - str: The formatted number
    """
    if n < 1000:
        return f"{int(n)} "
    if n < 1000000:
        return f"{(int(n / 100) / 10):.1f} k"
    if n < 1000000000:
        return f"{(int(n / 100000) / 10):.1f} M"
    return f"{(int(n / 100000000) / 10):.1f} G"
