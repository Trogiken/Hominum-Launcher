import traceback
from source.path import APPLICATION_PATH


def write_error_file(exc, val, tb):
    """Writes the error to a file"""
    error_file = APPLICATION_PATH / "error.txt"
    with open(error_file, "w") as f:
        f.write("".join(traceback.format_exception(exc, val, tb)))
    print("Error occurred, check error.txt for more information")
    print("For help send this file to Creme Fraiche on discord")


class InvalidModsPath(Exception):
    """Raised when the mods path is invalid"""
    pass
