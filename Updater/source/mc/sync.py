"""This module contains the sync functionality for the Hominum Client program."""
import os
from source.mc import remote
from source import exceptions


def sync_dir(local_dir: str, remote_dir: str) -> None:
    """
    Syncs mods with the server.

    Parameters:
    - local_dir (str): The local directory to sync.
    - remote_dir (str): The remote directory to sync.
        Options: "config", "mods", "resourcepacks", "shaderpacks"

    Exceptions:
    - Exception: If any other error occurs.

    Returns:
    - None
    """
    print("\n**** Syncing Mods ****")
    try:
        config = remote.get_config()
        remote_dir_url = config["urls"][remote_dir]
        server_mods = remote.get_filenames(config["urls"][remote_dir_url])  # TODO: Error handling

        # Remove mods that are not on the server
        print("\nRemoving Invalid Mods...")
        invalid_mod_count = 0
        for file in os.listdir(local_dir):
            if file not in server_mods:
                os.remove(os.path.join(local_dir, file))
                print(f"Removed '{file}'")
                invalid_mod_count += 1
        print(f"Removed {invalid_mod_count} invalid mod(s)")

        # Download mods from the server that arn't in the local mods folder
        print("\nDownloading new mods...")
        total_downloaded = remote.download_files(
            remote.get_file_downloads(remote_dir_url), local_dir
        )
        print(f"Finished downloading {total_downloaded} mod(s)")

        # Validate the mods directory after syncing
        print("\nValidating mod directory...")
        local_mod_files = os.listdir(local_dir)
        invalid = False
        for file in local_mod_files:
            if file not in server_mods:
                print(f"INVALID: '{file}'")
                invalid = True
        for file in server_mods:
            if file not in local_mod_files:
                print(f"MISSING: '{file}'")
                invalid = True
        if invalid:
            raise exceptions.InvalidModsPath()
        print("Directory Valid")

        print("\n**** Finished Syncing Mods ****")
    except Exception as e:
        print("\n**** Syncing Mods Failed ****")
        if isinstance(e, exceptions.InvalidModsPath):
            print("ERROR: Missing/Invalid Mods")
        else:
            raise e  # re-raise the exception if it's not an InvalidModsPath error


def sync_file(local_filepath: str, remote_file) -> None:
    """
    Syncs the specified file with the server.

    Parameters:
    - local_filepath (str): The local file to sync.
    - remote_file (str): The remote file to sync.
        Options: "options"
    
    Returns:
    - None
    """
    print("\n**** Syncing File ****")
    try:
        config = remote.get_config()
        remote_file_url = config["urls"][remote_file]
        server_file = remote.get_file_download(remote_file_url)

        # Remove the local file if it exists
        if os.path.exists(local_filepath):
            os.remove(local_filepath)
            print(f"Removed '{local_filepath}'")

        # Download the file from the server
        print("\nDownloading new file...")
        remote.download(server_file, local_filepath)
        print(f"Finished downloading '{local_filepath}'")

        print("\n**** Finished Syncing File ****")
    except Exception as e:
        print("\n**** Syncing File Failed ****")
        raise e  # re-raise the exception
