"""
This module contains the main class for handling Minecraft.

Classes:
- InstallWatcher: Observes and logs the installation process of a version install.
- MCManager: A class that handles Minecraft.
"""

import logging
import threading
import time
import os
from typing import Generator, List, Optional
import psutil
from source import exceptions, utils
from source.mc import remote
from source.portablemc.auth import MicrosoftAuthSession
from source.portablemc.standard import Watcher, Context, Version, SimpleWatcher, Environment, \
    DownloadStartEvent, DownloadProgressEvent, DownloadCompleteEvent, \
    VersionLoadingEvent, VersionFetchingEvent, VersionLoadedEvent, \
    JvmLoadingEvent, JvmLoadedEvent, JarFoundEvent, \
    AssetsResolveEvent, LibrariesResolvingEvent, LibrariesResolvedEvent, LoggerFoundEvent
from source.portablemc.fabric import FabricVersion, FabricResolveEvent
from source.portablemc.forge import ForgeVersion, ForgeResolveEvent, ForgePostProcessingEvent, \
    ForgePostProcessedEvent

logger = logging.getLogger(__name__)

# FIXME: Incorporate a thread watcher here that kills thread if they pause or if the program closes


class InstallWatcher(SimpleWatcher):
    """
    Observes and logs the installation process of a version install.
    This also prevents the installation process from idling.
    
    Attributes:
    app: A class, particurely the install frame that has methods to update the gui info.
    """
    def __init__(self, app) -> None:  # pylint: disable=too-many-statements
        def progress_task(key: str, **kwargs) -> None:
            if key == "start.version.loading":
                logger.debug("Loading version %s...", kwargs["version"])
            elif key == "start.version.fetching":
                logger.debug("Fetching version %s...", kwargs["version"])
            elif key == "start.jvm.loading":
                logger.debug("Loading JVM...")
            elif key == "start.libraries.resolving":
                logging.debug("Checking libraries...")
            elif key == "start.forge.post_processing":
                logger.debug("Forge post processing %s...", kwargs["task"])
            else:
                logger.debug("Progress task: %s", key)

        def finish_task(key: str, **kwargs) -> None:
            if key == "start.version.loaded":
                logger.info("Loaded version %s", kwargs["version"])
            elif key == "start.version.loaded.fetched":
                logger.info("Loaded version %s (fetched)", kwargs["version"])
            elif key == f"start.jvm.loaded.{JvmLoadedEvent.MOJANG}":
                logger.info("Loaded Mojang java %s", kwargs["version"])
            elif key == f"start.jvm.loaded.{JvmLoadedEvent.BUILTIN}":
                logger.info("Loaded builtin java %s", kwargs["version"])
            elif key == f"start.jvm.loaded.{JvmLoadedEvent.CUSTOM}":
                logger.info("Loaded custom java %s", kwargs["version"])
            elif key == "start.jar.found":
                logger.info("Checked version jar")
            elif key == "start.logger.found":
                logger.info("Using logger %s", kwargs["version"])
            elif key == "start.forge.post_processed":
                logger.info("Forge post processing done")
            else:
                logger.info("Finished task: %s", key)

        def assets_resolve(e: AssetsResolveEvent) -> None:
            if e.count is None:
                logger.debug("Resolving assets for version %s", e.index_version)
            else:
                logger.debug("Resolved %s assets for version %s", e.count, e.index_version)

        def libraries_resolved(e: LibrariesResolvedEvent) -> None:
            logger.debug(
                "Resolved %s class libraries and %s native libraries",
                e.class_libs_count, e.native_libs_count
            )

        def fabric_resolve(e: FabricResolveEvent) -> None:
            if e.loader_version is None:
                logger.debug("Resolving %s loader for %s", e.api.name, e.vanilla_version)
            else:
                logger.debug("Resolved %s loader for %s", e.api.name, e.vanilla_version)

        def forge_resolve(e: ForgeResolveEvent) -> None:
            api = "forge"
            if e.alias:
                logger.debug("Resolving %s alias %s", api, e.forge_version)
            else:
                logger.debug("Resolved %s %s", api, e.forge_version)

        super().__init__({
            VersionLoadingEvent: lambda e: progress_task(
                "start.version.loading", version=e.version
            ),
            VersionFetchingEvent: lambda e: progress_task(
                "start.version.fetching", version=e.version
            ),
            VersionLoadedEvent: lambda e: finish_task(
                "start.version.loaded.fetched" if e.fetched else "start.version.loaded",
                version=e.version
            ),
            JvmLoadingEvent: lambda e: progress_task("start.jvm.loading"),
            JvmLoadedEvent: lambda e: finish_task(
                f"start.jvm.loaded.{e.kind}", version=e.version or ""
            ),
            JarFoundEvent: lambda e: finish_task("start.jar.found"),
            AssetsResolveEvent: assets_resolve,
            LibrariesResolvingEvent: lambda e: progress_task("start.libraries.resolving"),
            LibrariesResolvedEvent: libraries_resolved,
            LoggerFoundEvent: lambda e: finish_task("start.logger.found", version=e.version),
            FabricResolveEvent: fabric_resolve,
            ForgeResolveEvent: forge_resolve,
            ForgePostProcessingEvent: lambda e: progress_task(
                "start.forge.post_processing", task=e.task
            ),
            ForgePostProcessedEvent: lambda e: finish_task("start.forge.post_processed"),
            DownloadStartEvent: self.download_start,
            DownloadProgressEvent: self.download_progress,
            DownloadCompleteEvent: self.download_complete,
        })

        self.app = app

        self.entries_count: int
        self.total_size: int
        self.speeds: List[float]
        self.sizes: List[int]
        self.size = 0

    def download_start(self, e: DownloadStartEvent):
        """
        Called when download starts.

        Sets up attributes and updates the title and progress bar.
        """
        self.entries_count = e.entries_count
        self.total_size = e.size
        self.speeds = [0.0] * e.threads_count
        self.sizes = [0] * e.threads_count
        self.size = 0

        self.app.update_title("Provisioning Environment")
        self.app.reset_progress()
        self.entries_count = self.entries_count

    def download_progress(self, e: DownloadProgressEvent) -> None:
        """
        Called when the threads have a progress event.
        
        Updates the progress bar and the item message with install info.
        """
        self.speeds[e.thread_id] = e.speed  # Store speed for later
        self.sizes[e.thread_id] = e.size  # Store size for later

        speed = sum(self.speeds)  # Sum speeds to get total speed
        total_count = str(self.entries_count)  # Total count of entries
        count = f"{e.count:{len(total_count)}}"  # Pad count with zeros
        size = f"{utils.format_number(self.size + sum(self.sizes))}B"  # Sum sizes to get total size
        speed = f"{utils.format_number(speed)}B/s"  # Format speed

        if e.done:
            logger.debug("File Downloaded: %s", e.entry)
            self.size += e.size

        item_msg = f"Total Downloaded: {size:>8} - {speed}"
        self.app.update_item(item_msg)
        self.app.update_progress(int(count) / int(total_count))

    def download_complete(self, _: DownloadCompleteEvent) -> None:
        """
        Called when all threads are done downloading.

        Updates the item message and sets the progress bar to indeterminate.
        """
        logger.info("Download complete")
        self.app.update_item("Download Complete")
        self.app.progress_indeterminate()


class Installation:
    def __init__(
            self, version: Version | FabricVersion | ForgeVersion, watcher: InstallWatcher
        ):
        self.version = version
        self.watcher = watcher

    def _is_process_idle(self, proc, threshold=1):
        # Check CPU usage of the process
        cpu_usage = proc.cpu_percent(interval=1)

        # Check IO usage of the process
        io_counters = proc.io_counters()
        read_count = io_counters.read_count
        write_count = io_counters.write_count
        time.sleep(1)
        new_io_counters = proc.io_counters()
        new_read_count = new_io_counters.read_count
        new_write_count = new_io_counters.write_count
        logger.debug(
            "Checked Idle: CPU: %s, Read: %s/%s, Write: %s/%s",
            cpu_usage, read_count, new_read_count, write_count, new_write_count
        )

        # Determine if process is idle based on CPU and IO usage
        is_idle = \
            cpu_usage < threshold\
            and read_count == new_read_count\
            and write_count == new_write_count
        return is_idle

    def download(self) -> None:
        """
        This is a rewrite of the install function in the PortableMC Version class
        """
        watcher = self.watcher

        # pylint: disable=protected-access
        self.version._dl.clear()
        self.version._applied_fixes.clear()

        self.version._resolve_version(watcher)
        self.version._resolve_metadata(watcher)
        self.version._resolve_features(watcher)
        self.version._resolve_jvm(watcher)
        self.version._resolve_jar(watcher)
        self.version._resolve_assets(watcher)
        self.version._resolve_libraries(watcher)
        self.version._resolve_logger(watcher)
        self.version._download(watcher)
        self.version._finalize_assets(watcher)
        # pylint: enable=protected-access

    def install(self) -> Environment:
        """
        Run and monitor install for idleness
        
        Exceptions:
        - VersionInstallTimeout: If the installation times out.

        Returns:
        - Environment: The environment for the version.
        """
        download_thread = threading.Thread(target=self.download)
        download_thread.start()

        start_time = time.time()
        process = psutil.Process(os.getpid())  # The current process
        check_interval = 5  # Seconds until next check
        timeout = 30  # Seconds until exception is raised while idle

        while download_thread.is_alive():
            if self._is_process_idle(process):
                logger.debug("Process is idle")
                if time.time() - start_time > timeout:
                    raise exceptions.VersionInstallTimeout("Install timed out")
            else:
                start_time = time.time()  # Reset the timer if not idle
            time.sleep(check_interval)

        return self.version._resolve_env(self.watcher)  # pylint: disable=protected-access


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
        Provisions an environment for the version to run.

        Parameters:
        - version (Version | FabricVersion | ForgeVersion): The version.
        - watcher (Watcher): The watcher for PortableMC. Defaults to None.

        Returns:
        - Environment: The environment for PortableMC.
        """
        # FIXME: Installation() still doesn't solve the issue of thread remaining after program close
        timeout_count = 0
        while True:
            try:
                # force install of normal game files
                vanilla_mc_version = self._create_vanilla_version(
                    self.remote_config["games"][self.game_selected]["mc_version"]
                )
                vanilla_mc = Installation(vanilla_mc_version, watcher)
                vanilla_mc.install()
                # Return actual environment requested
                version_install = Installation(version, watcher)
                return version_install.install()
            except exceptions.VersionInstallTimeout as timeout_error:
                if timeout_count > 3:
                    raise timeout_error
                timeout_count += 1
                continue
            except Exception as install_error:
                raise install_error

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
