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
import pickle
import tkinter
import tkinter.filedialog
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

SAVED_PATH = os.path.join(WORK_DIR, "mod_paths.pkl")


def get_saved_paths() -> list:
    """
    Return the saved paths if the file exists.

    Returns:
    - list: A list of saved paths if the file exists, otherwise an empty list.
    """
    try:
        with open(SAVED_PATH, "rb") as f:
            paths = pickle.load(f)
        return paths
    except FileNotFoundError:
        return []


def save_path(path: str) -> None:
    """
    Save the path to the SAVED_PATH file.

    Parmeters:
    path (str): The path to be saved.

    Returns:
    - None
    """
    paths = get_saved_paths()

    if path in paths:
        print("Path already saved")
        return

    paths.append(path)

    with open(SAVED_PATH, "wb") as f:
        pickle.dump(paths, f)


def is_valid_mod_path(path: str) -> bool:
    """
    Check if the path is valid to be used as the mods path.
    
    Parameters:
    path (str): The path to check.
        
    Returns:
    - bool: True if the path exists, False otherwise.
    """
    if not os.path.exists(path):
        return False

    return True


def get_mods_path() -> str:
    """
    Returns the path to the mods folder.

    Returns:
    - str: The path to the mods folder. If the path is not found, an empty string is returned.
    """
    if os.name == "nt":
        user_profile = os.getenv("USERPROFILE")
        base_path = os.path.join(user_profile, "curseforge", "minecraft", "Instances")
    elif os.name == "posix":
        user_profile = os.getenv("HOME")
        base_path = os.path.join(user_profile, "Games", "CurseForge", "Minecraft", "Instances")
    else:
        return ""

    server_pack_names = [
        "Serverstienpack",
        "Serverstienpack1",
        "Serverstienpack1.1",
        "Serverstienpack1.1(fixed)",
        "Serverstienpack-1.1",
        "Serverstienpack-1.1(fixed)",
        "serverstienpack",
        "serverstienpack1",
        "serverstienpack1.1",
        "serverstienpack1.1(fixed)",
        "serverstienpack-1.1",
        "serverstienpack-1.1(fixed)",
        "Serverstien",
        "Serverstien1",
        "Serverstien1.1",
        "Serverstien1.1(fixed)",
        "Serverstien-1.1",
        "Serverstien-1.1(fixed)",
        "serverstien",
        "serverstien1",
        "serverstien1.1",
        "serverstien1.1(fixed)",
        "serverstien-1.1",
        "serverstien-1.1(fixed)",
        "Serverstienpack 1",
        "Serverstienpack 1.1",
        "Serverstienpack 1.1(fixed)",
        "Serverstienpack - 1.1",
        "Serverstienpack - 1.1(fixed)",
        "serverstienpack 1",
        "serverstienpack 1.1",
        "serverstienpack 1.1(fixed)",
        "serverstienpack - 1.1",
        "serverstienpack - 1.1(fixed)",
        "Serverstien 1",
        "Serverstien 1.1",
        "Serverstien 1.1(fixed)",
        "Serverstien - 1.1",
        "Serverstien - 1.1(fixed)",
        "serverstien 1",
        "serverstien 1.1",
        "serverstien 1.1(fixed)",
        "serverstien - 1.1",
        "serverstien - 1.1(fixed)",
    ]

    paths_to_try = [os.path.join(base_path, pack_name, "mods") for pack_name in server_pack_names]
    paths_to_try.extend(get_saved_paths())

    for mods_path in paths_to_try:
        if is_valid_mod_path(mods_path):
            return mods_path

    return ""


def get_path_tk() -> str:
    """Return path using tk file dialog"""
    while True:
        path = tkinter.filedialog.askdirectory(title="Select the mods folder")
        if not path:
            print("Operation cancelled.")
            return ""
        if is_valid_mod_path(path):
            return path
        print("Invalid mod path, please select again.")
