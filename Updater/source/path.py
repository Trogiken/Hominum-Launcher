"""
This module contains the paths used by the launcher.

Constants:
- PROGRAM_NAME (str): The name of the program.
- PROGRAM_NAME_LONG (str): The long name of the program.
- VERSION (str): The version of the program.
- APPLICATION_DIR (pathlib.Path): The directory of the application.
- ASSETS_DIR (pathlib.Path): The directory of the assets.
- STORE_DIR (pathlib.Path): The directory of the store.
- MAIN_DIR (pathlib.Path): The directory of the main data.
- WORK_DIR (pathlib.Path): The directory of the working data.
- CONTEXT (Context): The context of the program.
"""

# TODO: Rename this module to constants

import os
import pathlib
import sys
from portablemc.standard import Context

PROGRAM_NAME = "Hominum"
PROGRAM_NAME_LONG = "Hominum Launcher"
VERSION = "4.6.3.4"

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
