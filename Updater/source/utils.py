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
# from source import path


SETTINGS_FILENAME = "settings.pkl"
# SETTINGS_PATH = pathlib.Path(os.path.join(path.STORE_DIR, SETTINGS_FILENAME))
SETTINGS_PATH = pathlib.Path(os.path.join(pathlib.Path(__file__).parents[1], SETTINGS_FILENAME))


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



# TODO: Turn this into a normal class and put the module functions in it
class Settings:
    def __init__(self):
        self._gui = GUISettings()
        self._user = UserSettings()
        self._game = GameSettings()
        self.read_settings()

    def read_settings(self):
        try:
            with open(SETTINGS_PATH, 'rb') as f:
                data = pickle.load(f)
                self._gui = data.get('gui', GUISettings())
                self._user = data.get('user', UserSettings())
                self._game = data.get('game', GameSettings())
        except FileNotFoundError:
            self.write_settings()

    def write_settings(self):
        data = {
            'gui': self._gui,
            'user': self._user,
            'game': self._game,
        }
        with open(SETTINGS_PATH, 'wb') as f:
            pickle.dump(data, f)
        self.read_settings()

    @property
    def gui(self):
        return self._gui

    @gui.setter
    def gui(self, value):
        self._gui = value
        self.write_settings()

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):
        self._user = value
        self.write_settings()

    @property
    def game(self):
        return self._game

    @game.setter
    def game(self, value):
        self._game = value
        self.write_settings()

    def update_gui(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self._gui, key, value)
        self.write_settings()

    def update_user(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self._user, key, value)
        self.write_settings()

    def update_game(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self._game, key, value)
        self.write_settings()


# def get_image(image_name: str) -> Image.Image:
#     """
#     Get the image from the assets directory.

#     Parameters:
#     - image_name (str): The name of the image.

#     Returns:
#     - Image: The image.
#     """
#     return Image.open(path.ASSETS_DIR / "images" / image_name)



settings = Settings()

print(settings.gui.font)
print(settings.user.email)
print(settings.game.jvm_args)

settings.update_gui(font_size_normal=20)  # FIXME: Doesnt change font size for line 166
settings.update_user(email="test")
settings.update_game(jvm_args=["-Xmx4G"])

print(settings.gui.font)
print(settings.user.email)
print(settings.game.jvm_args)
