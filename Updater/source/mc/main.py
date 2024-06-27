"""
This module contains the main class for handling Minecraft.

Classes:
- MCManager: A class that handles Minecraft.
"""

import os
from typing import Generator
from source.mc import remote
from portablemc.standard import Context, Environment, Watcher
from portablemc.fabric import FabricVersion


class MCManager:
    """MCManager is a class that handles Minecraft"""
    def __init__(self, context: Context):
        self.context = context
        self.remote_config = remote.get_config()

        self.server_ip: str = self.remote_config["client"]["server_ip"]
        self.fabric_version: str = self.remote_config["client"]["fabric_version"]
        self.loader_version: str = self.remote_config["client"]["loader_version"]

    def provision_version(self, vanilla_version: str, loader_version: str=None) -> FabricVersion:
        """
        Provisions a version for PortableMC.

        Parameters:
        - vanilla_version (str): The fabric version.
        - loader_version (str): The loader version. Defaults to latest.

        Returns:
        - FabricVersion: The version for PortableMC.
        """
        return FabricVersion.with_fabric(
            vanilla_version=vanilla_version, loader_version=loader_version, context=self.context
        )

    def provision_environment(self, version: FabricVersion, watcher: Watcher=None) -> Environment:
        """
        Provisions an environment for PortableMC.

        Parameters:
        - version (FabricVersion): The version for PortableMC.
        - watcher (Watcher): The watcher for PortableMC. Defaults to None.

        Returns:
        - Environment: The environment for PortableMC.
        """
        return version.install(watcher=watcher)

    def sync_dir(self, remote_dir: str) -> Generator[tuple, None, None]:
        """
        Syncs mods with the server.

        Parameters:
        - remote_dir (str): The remote directory to sync.
            Options: "config", "mods", "resourcepacks", "shaderpacks"

        Exceptions:
        - Exception: If any other error occurs.

        Returns:
        - Generator[tuple, None, None]: A generator that yields the progress of the sync.
        """
        if remote_dir not in self.remote_config["urls"]:
            raise ValueError(f"Invalid remote directory: {remote_dir}")
        if remote_dir == "config":
            local_dir = self.context.work_dir / "config"
        elif remote_dir == "mods":
            local_dir = self.context.work_dir / "mods"
        elif remote_dir == "resourcepacks":
            local_dir = self.context.work_dir / "resourcepacks"
        elif remote_dir == "shaderpacks":
            local_dir = self.context.work_dir / "shaderpacks"
        else:
            raise ValueError(f"Unknown valid remote directory: {remote_dir}")
        try:
            os.makedirs(local_dir, exist_ok=True)
        except Exception:
            # TODO: Add error handling
            pass
        try:
            remote_dir_url = self.remote_config["urls"][remote_dir]
            if remote_dir_url is None:
                return
            server_mods = remote.get_filenames(remote_dir_url)  # TODO: Error handling
            # Remove invalid mods
            for file in os.listdir(local_dir):
                if file not in server_mods:
                    os.remove(os.path.join(local_dir, file))

            # Download mods
            urls_to_download = remote.get_file_downloads(remote_dir_url)
            for count, total, filename in remote.download_files(urls_to_download, local_dir):
                yield (count, total, filename)
        except Exception:
            # TODO: Add error handling
            pass

    def sync_file(self, remote_file) -> None:
        """
        Syncs the specified file with the server.

        Parameters:
        - remote_file (str): The remote file to sync.
            Options: "options", "servers"

        Returns:
        - None
        """
        if remote_file not in self.remote_config["urls"]:
            raise ValueError(f"Invalid remote file: {remote_file}")
        if remote_file == "options":
            local_filepath = self.context.work_dir / "options.txt"
        elif remote_file == "servers":
            local_filepath = self.context.work_dir / "servers.dat"
        else:
            raise ValueError(f"Unknown valid remote file: {remote_file}")
        try:
            os.makedirs(os.path.dirname(local_filepath), exist_ok=True)
        except Exception:
            # TODO: Add error handling
            pass

        try:
            remote_file_url = self.remote_config["urls"][remote_file]
            if remote_file_url is None:
                return
            server_file = remote.get_file_download(remote_file_url)

            # Remove the local file if it exists
            if os.path.exists(local_filepath):
                os.remove(local_filepath)

            # Download the file from the server
            remote.download(server_file, local_filepath)
        except Exception:
            # TODO: Add error handling
            pass
