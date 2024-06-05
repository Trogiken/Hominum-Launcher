"""
This module provides functions related to file paths and directories.

It includes functions to retrieve saved paths, save a new path, check if a path is valid,
get the path to the mods folder, and get a path using the tk file dialog.

Functions:
- get_saved_paths(): Return the saved paths if the file exists.
- save_path(path: str): Pickle the path to the file.
- is_valid_mod_path(path: str): Returns True if the entered path exists and all files in the directory are jars.
- get_mods_path(): Returns the path to the mods folder.
- get_path_tk(): Return path using tk file dialog.

Constants:
- USER_APP_PATH: The path to the user application folder.
- SAVED_PATH: The path to the saved paths file.
- APPLICATION_PATH: The path to the application.
"""

import os
import pathlib
import sys
import pickle
import tkinter
import tkinter.filedialog

if getattr(sys, 'frozen', False):
    APPLICATION_PATH = pathlib.Path(sys.executable).parent
else:
    APPLICATION_PATH = pathlib.Path(__file__).parent

if os.name == "nt":
    USER_APP_PATH = os.path.join(os.getenv("APPDATA"), "Hominum-Updater")
elif os.name == "posix":
    USER_APP_PATH = os.path.join(os.getenv("HOME"), ".hominum-updater")
else:
    USER_APP_PATH = os.path.join(APPLICATION_PATH, "user_data")
SAVED_PATH = os.path.join(USER_APP_PATH, "mod_paths.pkl")

try:
    if not os.path.exists(USER_APP_PATH):
        os.makedirs(USER_APP_PATH)
except Exception:
    from source.exceptions import write_error_file  # prevent circular import
    write_error_file(*sys.exc_info())


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
    - bool: True if the path exists and all files in the directory are jars, False otherwise.
    """
    if not os.path.exists(path):
        return False

    if all(file.endswith('.jar') for file in os.listdir(path)):
        return True
    else:
        return False


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
        else:
            print("Invalid mod path, please select again.")
