"""
This module contains the main class for handling Minecraft.

Classes:
- MCManager: A class that handles Minecraft.
"""

import logging
import os
from typing import Generator
from source.mc import remote
from portablemc.auth import MicrosoftAuthSession
from portablemc.standard import Context, Environment, Watcher, Version
from portablemc.fabric import FabricVersion
from portablemc.forge import ForgeVersion

logger = logging.getLogger(__name__)


class MCManager:
    """
    MCManager is a class that handles Minecraft

    Attributes:
    - context (Context): The context for PortableMC.
    - remote_config (dict): The remote configuration.
    - server_ip (str): The server IP.
    - game_selected (str): The selected game/mc-version (Vanilla, Fabric, etc)

    Methods:
    - provision_version: Provisions a version.
    - provision_environment: Provisions an environment.
    - sync_dir: Syncs mods with the server.
    - sync_file: Syncs the specified file with the server
    """
    def __init__(self, context: Context):
        logger.debug("Initializing MCManager")

        self.context = context
        self.remote_config = remote.get_config()

        self.server_ip: str = self.remote_config.get("startup", {}).get("server_ip", "")
        self.game_selected: str = self.remote_config.get("startup", {}).get("game", "")

        logger.debug("Context: %s", self.context)
        logger.debug("Remote Config: %s", self.remote_config)
        logger.debug("Server IP: %s", self.server_ip)
        logger.debug("Game Selected: %s", self.game_selected)

        logger.debug("MCManager initialized")

    def _create_dir_path(self, remote_dir: str) -> tuple:
        """
        Creates the local and remote directory paths.

        Parameters:
        - remote_dir (str): The remote directory to sync.
            Options: "config", "mods", "resourcepacks", "shaderpacks"

        Exceptions:
        - ValueError: If the remote directory is invalid.
        - ValueError: If the remote directory URL is not set.

        Returns:
        - tuple: The local directory path and the remote directory URL.
        """
        if self.remote_config is None:
            raise ValueError("Remote config is not set")
        if remote_dir not in self.remote_config["urls"]:
            raise ValueError(f"Invalid remote directory: {remote}")
        if remote_dir == "config":
            local_dir = self.context.work_dir / "config"
        elif remote_dir == "mods":
            local_dir = self.context.work_dir / "mods"
        elif remote_dir == "resourcepacks":
            local_dir = self.context.work_dir / "resourcepacks"
        elif remote_dir == "shaderpacks":
            local_dir = self.context.work_dir / "shaderpacks"
        else:
            raise ValueError(f"Unknown valid remote directory: {remote}")

        local_dir.mkdir(parents=True, exist_ok=True)
        remote_dir_url = self.remote_config["urls"][remote_dir]
        logger.debug("Remote directory URL: %s", remote_dir_url)

        return local_dir, remote_dir_url

    def _create_file_path(self, remote_file: str) -> tuple:
        """
        Creates the local and remote file paths.
        
        Parameters:
        - remote_file (str): The remote file to sync.
            Options: "options", "servers"

        Exceptions:
        - ValueError: If the remote file is invalid.
        - ValueError: If the remote file URL is not set.

        Returns:
        - tuple: The local file path and the remote file URL.
        """
        if remote_file not in self.remote_config["urls"]:
            raise ValueError(f"Invalid remote file: {remote_file}")
        if remote_file == "options":
            local_filepath = self.context.work_dir / "options.txt"
        elif remote_file == "servers":
            local_filepath = self.context.work_dir / "servers.dat"
        else:
            raise ValueError(f"Unknown valid remote file: {remote_file}")

        os.makedirs(os.path.dirname(local_filepath), exist_ok=True)
        remote_file_url = self.remote_config["urls"][remote_file]
        logger.debug("Remote file URL: %s", remote_file_url)

        return local_filepath, remote_file_url

    def _create_vanilla_version(self, mc_version: str=None) -> Version:
        """
        Create vanilla root.

        Parameters:
        - mc_version (str): Version of Minecraft.

        Returns:
        - Version: Vanilla version.
        """
        logger.debug("mc_version: %s", mc_version)
        return Version(version=mc_version, context=self.context)

    def _create_fabric_version(
            self, mc_version: str=None, loader_version: str=None
        ) -> FabricVersion:
        """
        Create fabric root.
        
        Parameters:
        - mc_version (str): Version of Minecraft.
        - loader_version (str): Version of the loader.

        Returns
        - FabricVersion: Fabric version.
        """
        logger.debug("mc_version: %s", mc_version)
        logger.debug("loader_version: %s", loader_version)
        if mc_version is None:
            mc_version = "release"
        return FabricVersion.with_fabric(
            vanilla_version=mc_version, loader_version=loader_version, context=self.context
        )

    def _create_quilt_version(
            self, mc_version: str=None, loader_version: str=None
        ) -> FabricVersion:
        """
        Create quilt root.
        
        Parameters:
        - mc_version (str): Version of Minecraft.
        - loader_version (str): Version of the loader.

        Returns
        - FabricVersion: Quilt version.
        """
        logger.debug("mc_version: %s", mc_version)
        logger.debug("loader_version: %s", loader_version)
        if mc_version is None:
            mc_version = "release"
        return FabricVersion.with_quilt(
            vanilla_version=mc_version, loader_version=loader_version, context=self.context
        )

    def _create_forge_version(self, mc_version: str=None, forge_version: str=None) -> ForgeVersion:
        """
        Create forge root.
        
        Parameters:
        - mc_version (str): Version of Minecraft.
        - forge_version (str): Version of forge.

        Returns
        - ForgeVersion: Forge version.
        """
        logger.debug("mc_version: %s", mc_version)
        logger.debug("forge_version: %s", forge_version)
        if forge_version is None:
            forge_version = "recommended"

        forge = f"{mc_version}-{forge_version}"
        if mc_version is None:
            forge = "release"
            logger.warning("Forge MC version set to None, ignoring forge version")
        return ForgeVersion(forge_version=forge, context=self.context)

    def provision_version(
            self, auth_session: MicrosoftAuthSession, autojoin: bool
        ) -> Version | FabricVersion | ForgeVersion:
        """
        Provisions a version based on server

        Parameters:
        - auth_session (MicrosoftAuthSession): Auth session to add to version
        - autojoin (bool): Place user in server on startup

        Returns:
        Version | FabricVersion | ForgeVersion: The version set by the server
        """
        logger.debug("auth_session: %s", auth_session)
        logger.debug("autojoin: %s", autojoin)
        if self.remote_config is None:
            raise ValueError("Remote config is not set")

        games = self.remote_config["games"]
        if self.game_selected not in games:
            raise ValueError(f"Invalid game selected: {self.game_selected}")
        game_config = games[self.game_selected]

        if self.game_selected == "vanilla":
            version = self._create_vanilla_version(
                mc_version=game_config["mc_version"]
            )
        elif self.game_selected == "fabric":
            version = self._create_fabric_version(
                mc_version=game_config["mc_version"], loader_version=game_config["loader_version"]
            )
        elif self.game_selected == "quilt":
            version = self._create_quilt_version(
                mc_version=game_config["mc_version"], loader_version=game_config["loader_version"]
            )
        elif self.game_selected == "forge":
            version = self._create_forge_version(
                mc_version=game_config["mc_version"], forge_version=game_config["forge_version"]
            )
        else:
            raise ValueError(f"Unknown valid game selected: {self.game_selected}")

        version.auth_session = auth_session
        if autojoin:
            version.set_quick_play_multiplayer(self.server_ip)
        logger.debug("Version: %s", version)

        return version

    def provision_environment(
            self, version: Version | FabricVersion | ForgeVersion, watcher: Watcher=None
        )-> Environment:
        """
        Provisions an environment for the version to run

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
        local_dir, remote_dir_url = self._create_dir_path(remote_dir)
        if remote_dir_url is None:
            logger.warning("Remote directory '%s' is not set", remote_dir)
            return
        server_mods = remote.get_filenames(remote_dir_url)
        if server_mods is None:
            raise ValueError("Server filenames are not set")
        # Remove invalid mods
        for file in os.listdir(local_dir):
            if file not in server_mods:
                file_path = os.path.join(local_dir, file)
                os.remove(file_path)
                logger.info("Invalid mod '%s' removed", file_path)

        # Download mods
        urls_to_download = remote.get_file_downloads(remote_dir_url)
        if urls_to_download is None:
            raise ValueError("URLs to download are not set")
        for count, total, filename, error_occured in remote.download_files(
            urls_to_download, local_dir
        ):
            yield (count, total, filename, error_occured)

    def sync_file(self, remote_file) -> None:
        """
        Syncs the specified file with the server.

        Parameters:
        - remote_file (str): The remote file to sync.
            Options: "options", "servers"

        Returns:
        - None
        """
        local_filepath, remote_file_url = self._create_file_path(remote_file)
        if remote_file_url is None:
            logger.warning("Remote file '%s' is not set", remote_file)
            return
        server_file = remote.get_file_download(remote_file_url)
        if server_file is None:
            raise ValueError("Server file is not set")

        # Remove the local file if it exists
        if os.path.exists(local_filepath):
            os.remove(local_filepath)
            logger.info("Removed existing local file '%s'", local_filepath)

        # Download the file from the server
        remote.download(server_file, local_filepath)
