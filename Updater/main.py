import source as src
import pathlib
import traceback
import sys
import os
import tkinter
import tkinter.filedialog
from time import sleep

PROGRAM_NAME = "Hominum Modpack Updater"
VERSION = "1.3"
PATH_URL = r"https://raw.githubusercontent.com/Eclik1/Hominum-Updates/main/path.txt"
GITHUB_CONTENTS_BASE = r"https://api.github.com/repos/Eclik1/Hominum-Updates/contents"

# create the application path depending on if the script is an executable or not
if getattr(sys, 'frozen', False):
    APPLICATION_PATH = pathlib.Path(sys.executable).parent
else:
    APPLICATION_PATH = pathlib.Path(__file__).parent


class CustomTk(tkinter.Tk):
    def report_callback_exception(self, exc, val, tb):
        error_file = APPLICATION_PATH / "error.txt"
        with open(error_file, "w") as f:
            f.write("".join(traceback.format_exception(exc, val, tb)))
        print("Error occurred, check error.txt for more information")
        print("For help send this file to Creme Fraiche on discord")

    def destroy(self):
        self.quit()
        self.update()
        super().destroy()


def get_url_dir() -> str:
    """Returns url of the directory with mods"""
    resp = src.get_request(PATH_URL)
    path = resp.text.split("\n")[0].strip()
    url = f"{GITHUB_CONTENTS_BASE}/{path}"

    return url


def get_filenames() -> list:
    """Returns a list of mod names"""
    resp = src.get_request(get_url_dir())
    names = []
    for file in resp.json():
        names.append(file["name"])

    return names


def get_file_downloads() -> list:
    """Returns a list of download urls"""
    resp = src.get_request(get_url_dir())
    download_urls = []
    for file in resp.json():
        download_urls.append(file["download_url"])
    
    return download_urls


def is_valid_mod_path(path: str) -> bool:
    """Returns True if the entered path exists and all files in the directory are jars"""
    if not os.path.exists(path):
        return False

    if all(file.endswith('.jar') for file in os.listdir(path)):
        return True
    else:
        return False


def get_mods_path() -> str:
    """Returns the path to the mods folder"""
    user_profile = os.getenv("USERPROFILE")
    base_path = os.path.join(user_profile, "curseforge", "minecraft", "Instances")
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
    ]

    paths_to_try = [os.path.join(base_path, pack_name, "mods") for pack_name in server_pack_names]

    for mods_path in paths_to_try:
        if is_valid_mod_path(mods_path):
            return mods_path

    return ""


def get_path_tk() -> str:
    """Return path using tk file dialog"""
    while True:
        root = tkinter.Tk()
        root.withdraw()
        path = tkinter.filedialog.askdirectory(title="Select the mods folder")
        if not path:
            print("Operation cancelled.")
            return ""
        if is_valid_mod_path(path):
            return path
        else:
            print("Invalid mod path, please select again.")


def sync_mods(mods_path: str, ) -> None:
    """Syncs mods with the server"""
    print("\n**** Syncing Mods ****")
    print("Removing Invalid Mods...")
    server_mods = get_filenames()
    invalid_mod_count = 0
    for file in os.listdir(mods_path):
        if file not in server_mods:
            os.remove(os.path.join(mods_path, file))
            print(f"Removed '{file}'")
            invalid_mod_count += 1
    print(f"Removed {invalid_mod_count} invalid mod(s)")

    print("\nDownloading new mods...")
    total_downloaded = src.download_files(get_file_downloads(), mods_path)
    print(f"Finished downloading {total_downloaded} mod(s)")

    success = True
    for file in os.listdir(mods_path):
        if file not in server_mods:
            print(f"Warning: '{file}' is not on the server")
            success = False
    
    if success:
        print("**** Finished Syncing Mods ****")
    else:
        print("**** Failed To Sync Mods ****")


def main():
    """GUI part of the program"""
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
    mods_path = get_mods_path()
    PADDING = 20 # padding for the label
    MAX_LEN = 100 # max length of the path to display
    mods_path_label = tkinter.Label(root, font=("Arial", 12), wraplength=WINDOW_WIDTH - PADDING, justify="left")
    mods_path_label.pack(pady=5)
    if not mods_path:
        print("Mods folder not found, open it manually\nSee modpack-installation channel for info")
        mods_path_label.config(text="Unkown Mods Path")
        mods_path = get_path_tk()
        if mods_path:
            print(f"Updated mods path to {mods_path}")
        else:
            print("No valid mods path provided. Exiting...")
            sleep(3)
            return
    mods_path_text = mods_path
    if len(mods_path_text) > MAX_LEN:
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
