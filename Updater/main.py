"""
This module contains the main functionality for the Hominum Modpack Updater program.
It provides a GUI interface for syncing mods with a server.

Functions:
- sync_mods(mods_path: str) -> None: Syncs mods with the server.
- main() -> None: Runs the main GUI program.

Constants:
- PROGRAM_NAME: The name of the program.
- VERSION: The version of the program.
"""

import source as src
import sys
import os
import tkinter
import tkinter.filedialog
from time import sleep

PROGRAM_NAME = "Hominum Modpack Updater"
VERSION = "1.5"


class CustomTk(tkinter.Tk):
    def report_callback_exception(self, exc, val, tb):
        """Is called when an exception is raised in the GUI. Writes the error to a file."""
        src.exceptions.write_error_file(exc, val, tb)

    def destroy(self):
        """Called when the window is destroyed. Closes the window and exits the program."""
        self.quit()
        self.update()
        super().destroy()


def sync_mods(mods_path: str) -> None:
    """
    Syncs mods with the server.

    Parameters:
    - mods_path (str): The path to the mods directory.

    Exceptions:
    - Exception: If any other error occurs.

    Returns:
    - None
    """
    print("\n**** Syncing Mods ****")
    try:
        server_mods = src.download.get_filenames()

        # Remove mods that are not on the server
        print("\nRemoving Invalid Mods...")
        invalid_mod_count = 0
        for file in os.listdir(mods_path):
            if file not in server_mods:
                os.remove(os.path.join(mods_path, file))
                print(f"Removed '{file}'")
                invalid_mod_count += 1
        print(f"Removed {invalid_mod_count} invalid mod(s)")

        # Download mods from the server that arn't in the local mods folder
        print("\nDownloading new mods...")
        total_downloaded = src.download.download_files(
            src.download.get_file_downloads(), mods_path
        )
        print(f"Finished downloading {total_downloaded} mod(s)")

        # Validate the mods directory after syncing
        print("\nValidating mod directory...")
        invalid = False
        for file in os.listdir(mods_path):
            if file not in server_mods:
                print(f"Warning: '{file}' is not on the server")
                invalid = True
        if invalid:
            raise src.exceptions.InvalidModsPath()
        else:
            print("Directory is valid")

        print("\n**** Finished Syncing Mods ****")
    except Exception as e:
        print("\n**** Syncing Mods Failed ****")
        if isinstance(e, src.exceptions.InvalidModsPath):
            print("Error: Invalid mods detected after sync")
        else:
            raise e  # re-raise the exception if it's not an InvalidModsPath error


def main():
    """
    GUI portion of the program.

    This function creates a graphical user interface for the program.
    It sets up the window, labels, buttons, and runs the main event loop.

    Returns:
    - None
    """
    root = CustomTk()
    root.title(PROGRAM_NAME)

    WINDOW_WIDTH = 400
    WINDOW_HEIGHT = 150
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    root.resizable(False, False)

    # Title label
    title = tkinter.Label(root, text=PROGRAM_NAME, font=("Arial", 16))
    title.pack(pady=5)
    ########################

    # Mods path label
    mods_path = src.path.get_mods_path()
    PADDING = 20 # padding for the label
    MAX_LEN = 100 # max length of the path to display
    mods_path_label = tkinter.Label(root, text="", font=("Arial", 12), wraplength=WINDOW_WIDTH - PADDING, justify="left")
    mods_path_label.pack(pady=5)
    if not mods_path:
        print("Mods folder not found, open it manually\nSee modpack-installation channel for info")
        mods_path_label.config(text="Unkown Mods Path")
        mods_path = src.path.get_path_tk()
        if mods_path:
            try:
                src.path.save_path(mods_path)
                print("Saved new mods path")
            except Exception:
                src.exceptions.write_error_file(*sys.exc_info())
                print(f"Failed to save unknown mods path")
            print(f"Updated mods path to {mods_path}")
        else:
            print("No valid mods path provided. Exiting...")
            sleep(3)
            return
    mods_path_text = mods_path
    if len(mods_path_text) > MAX_LEN:  # shorten the path if it's too long
        mods_path_text = mods_path_text[:MAX_LEN] + "..."
    mods_path_label.config(text=mods_path_text)
    ########################

    # create update button
    button = tkinter.Button(
        root,
        text="Sync Modpack",
        font=("Arial", 12),
        height=1,
        width=15,
        command=lambda: sync_mods(mods_path)
    )
    button.pack(pady=1)
    ########################

    # create version label
    version_label = tkinter.Label(root, text=f"v{VERSION}", font=("Arial", 10))
    version_label.pack(side="bottom", anchor="se")
    ########################

    # run the mainloop
    root.mainloop()


if __name__ == '__main__':
    main()
