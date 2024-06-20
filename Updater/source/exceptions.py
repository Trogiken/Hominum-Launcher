"""
This module contains custom exceptions and functions related to error handling.

Functions:
- write_error_file(exc, val, tb) -> None: Writes the error to a file.

Exceptions:
- InvalidModsPath: Raised when the mods path is invalid.
"""

import traceback
from source.path import APPLICATION_DIR


def write_error_file(exc, val, tb) -> None:
    """
    Writes the error to a file.

    Parameters:
    - exc (type): The type of the exception.
    - val (Exception): The exception instance.
    - tb (traceback): The traceback object.

    Returns:
    - None
    """
    error_file = APPLICATION_DIR / "error.txt"
    with open(error_file, "w", encoding='utf-8') as f:
        f.write("".join(traceback.format_exception(exc, val, tb)))
    print("Error occurred, check error.txt for more information")
    print("For help send this file to Creme Fraiche on discord")


class InvalidModsPath(Exception):
    """
    Raised when the mods path is invalid.
    """


class AuthenticationFailed(Exception):
    """
    Raised when the microsoft authentication fails.
    """
