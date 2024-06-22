"""This module contains the sync functionality for the Hominum Client program."""
import os
import source as src


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
        local_mod_files = os.listdir(mods_path)
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
            raise src.exceptions.InvalidModsPath()
        print("Directory Valid")

        print("\n**** Finished Syncing Mods ****")
    except Exception as e:
        print("\n**** Syncing Mods Failed ****")
        if isinstance(e, src.exceptions.InvalidModsPath):
            print("ERROR: Missing/Invalid Mods")
        else:
            raise e  # re-raise the exception if it's not an InvalidModsPath error
