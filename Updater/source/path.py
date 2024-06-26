"""
This module provides functions related to file paths and directories.

It includes functions to retrieve saved paths, save a new path, check if a path is valid,
get the path to the mods folder, and get a path using the tk file dialog.

Functions:
- get_saved_paths() -> list: Return the saved paths if the file exists.
- save_path(path: str) -> None: Save the path to the SAVED_PATH file.
- is_valid_mod_path(path: str) -> bool: Check if the path is valid to be used as the mods path.
- get_mods_path() -> str: Returns the path to the mods folder.
- get_path_tk() -> str: Return path using tk file dialog

Constants:
- WORK_DIR: The path to the user application folder.
- SAVED_PATH: The path to the saved paths file.
- APPLICATION_DIRH: The path to the application directory.
"""

# TODO: Rename this module to constants

import os
import pathlib
import sys
from portablemc.standard import Context

PROGRAM_NAME = "Hominum"
PROGRAM_NAME_LONG = "Hominum Launcher"
VERSION = "4.5.3.4"

if getattr(sys, 'frozen', False):
    APPLICATION_DIR = pathlib.Path(sys.executable).parent
else:
    APPLICATION_DIR = pathlib.Path(__file__).parents[1]

ASSETS_DIR = pathlib.Path(os.path.join(APPLICATION_DIR, "assets"))

if os.name == "posix":
    STORE_DIR = os.path.join(os.getenv("HOME"), ".hominum")
else:
    STORE_DIR = os.path.join(APPLICATION_DIR, "Store")

STORE_DIR = pathlib.Path(STORE_DIR)
MAIN_DIR = pathlib.Path(os.path.join(STORE_DIR, "minecraft"))
WORK_DIR = pathlib.Path(os.path.join(STORE_DIR, "mcdata"))
CONTEXT = Context(MAIN_DIR, WORK_DIR)

os.makedirs(STORE_DIR, exist_ok=True)
os.makedirs(MAIN_DIR, exist_ok=True)
os.makedirs(WORK_DIR, exist_ok=True)
