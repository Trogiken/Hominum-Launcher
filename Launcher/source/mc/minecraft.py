"""
This module contains the main class for handling Minecraft.

Classes:
- MCManager: A class that handles Minecraft.
- InstallWatcher: A class that observes and logs the installation process of a version install.
- EnvironmentRunner: A class that updates the GUI.
"""

import logging
import time
import os
from pathlib import Path
from subprocess import Popen
from typing import Generator, List
from source import exceptions, utils, path
from source.mc import remote
from portablemc.auth import MicrosoftAuthSession
from portablemc.standard import Context, Version, SimpleWatcher, Environment, StandardRunner, \
    DownloadStartEvent, DownloadProgressEvent, DownloadCompleteEvent, \
    VersionLoadingEvent, VersionFetchingEvent, VersionLoadedEvent, \
    JvmLoadingEvent, JvmLoadedEvent, JarFoundEvent, \
    AssetsResolveEvent, LibrariesResolvingEvent, LibrariesResolvedEvent, LoggerFoundEvent
from portablemc.fabric import FabricVersion, FabricResolveEvent
from portablemc.forge import ForgeVersion, ForgeResolveEvent, ForgePostProcessingEvent, \
    ForgePostProcessedEvent

logger = logging.getLogger(__name__)

SETTINGS = utils.Settings()


class InstallWatcher(SimpleWatcher):
    """
    Observes and logs the installation process of a version install.
    This also prevents the installation process from idling.
    
    Attributes:
    app: A class, particurely the install frame that has methods to update the gui info.
    """
    def __init__(self, app) -> None:  # pylint: disable=too-many-statements
        self.app = app

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
                self.app.update_item(f"Post Processing: {kwargs['task']}")
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
                self.app.update_item("Post Processing Done")
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

        def func_resolve(func, *args, **kwargs) -> None:
            """Alias for calling a function with args and kwargs."""
            if os.path.exists(path.GLOBAL_KILL):
                raise exceptions.GlobalKill()
            func(*args, **kwargs)
            app.update_gui()

        super().__init__({
            VersionLoadingEvent: lambda e: func_resolve(
                progress_task, "start.version.loading", version=e.version
            ),
            VersionFetchingEvent: lambda e: func_resolve(
                progress_task, "start.version.fetching", version=e.version
            ),
            VersionLoadedEvent: lambda e: func_resolve(
                finish_task,
                "start.version.loaded.fetched" if e.fetched else "start.version.loaded",
                version=e.version
            ),
            JvmLoadingEvent: lambda e: func_resolve(progress_task, "start.jvm.loading"),
            JvmLoadedEvent: lambda e: func_resolve(
                finish_task, f"start.jvm.loaded.{e.kind}", version=e.version or ""
            ),
            JarFoundEvent: lambda e: func_resolve(
                finish_task, "start.jar.found"
            ),
            AssetsResolveEvent: lambda e: func_resolve(assets_resolve, e),
            LibrariesResolvingEvent: lambda e: func_resolve(
                progress_task, "start.libraries.resolving"
            ),
            LibrariesResolvedEvent: lambda e: func_resolve(libraries_resolved, e),
            LoggerFoundEvent: lambda e: func_resolve(
                finish_task, "start.logger.found", version=e.version
            ),
            FabricResolveEvent: lambda e: func_resolve(fabric_resolve, e),
            ForgeResolveEvent: lambda e: func_resolve(forge_resolve, e),
            ForgePostProcessingEvent: lambda e: func_resolve(
                progress_task, "start.forge.post_processing", task=e.task
            ),
            ForgePostProcessedEvent: lambda e: func_resolve(
                finish_task, "start.forge.post_processed"
            ),
            DownloadStartEvent: lambda e: self.object_func_resolve(self.download_start, e),
            DownloadProgressEvent: lambda e: self.object_func_resolve(self.download_progress, e),
            DownloadCompleteEvent: lambda e: self.object_func_resolve(self.download_complete, e),
        })

        self.app = app

        self.entries_count: int
        self.total_size: int
        self.speeds: List[float]
        self.sizes: List[int]
        self.size = 0

    def object_func_resolve(self, func, *args, **kwargs):
        """Alias for calling a function with args and kwargs."""
        if os.path.exists(path.GLOBAL_KILL):
            raise exceptions.GlobalKill()
        func(*args, **kwargs)

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


class EnvironmentRunner(StandardRunner):
    """
    A runner that updates the GUI.

    Attributes:
    - app: The app to update.
    """
    def __init__(self, app) -> None:
        self.app = app

    def process_wait(self, process: Popen) -> None:
        try:
            while process.poll() is None:
                self.app.update_gui()
                if self.app.kill_process:
                    raise exceptions.GlobalKill()
                time.sleep(0.1)
        except exceptions.GlobalKill:
            process.kill()
            raise
        finally:
            process.wait()
            self.app.on_run_complete()


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
        self.remote_tree = remote.get_repo_tree()
        self.remote_config = remote.get_config(self.remote_tree)

        if self.remote_config is None:
            raise exceptions.RemoteError("Remote config not found")
        if self.remote_tree is None:
            raise exceptions.RemoteError("Remote tree not found")

        self.server_ip: str = self.remote_config.get("startup", {}).get("server_ip", "")
        self.game_selected: str = self.remote_config.get("startup", {}).get("game", "")

        logger.debug("Context: %s", self.context)
        logger.debug("Remote Config: %s", self.remote_config)
        logger.debug("Server IP: %s", self.server_ip)
        logger.debug("Game Selected: %s", self.game_selected)

        logger.debug("MCManager initialized")

    def create_vanilla_version(self, mc_version: str=None) -> Version:
        """
        Create vanilla root.

        Parameters:
        - mc_version (str): Version of Minecraft.

        Returns:
        - Version: Vanilla version.
        """
        logger.debug("mc_version: %s", mc_version)
        return Version(version=mc_version, context=self.context)

    def create_fabric_version(
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

    def create_quilt_version(
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

    def create_forge_version(self, mc_version: str=None, forge_version: str=None) -> ForgeVersion:
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

    def provision_version(self, autojoin: bool) -> Version | FabricVersion | ForgeVersion:
        """
        Provisions a version based on server

        Parameters:
        - auth_session (MicrosoftAuthSession): Auth session to add to version
        - autojoin (bool): Place user in server on startup

        Returns:
        Version | FabricVersion | ForgeVersion: The version set by the server
        """
        logger.debug("autojoin: %s", autojoin)
        games = self.remote_config["games"]
        if self.game_selected not in games:
            raise ValueError(f"Invalid game selected: {self.game_selected}")
        game_config = games[self.game_selected]

        if self.game_selected == "vanilla":
            version = self.create_vanilla_version(
                mc_version=game_config["mc_version"]
            )
        elif self.game_selected == "fabric":
            version = self.create_fabric_version(
                mc_version=game_config["mc_version"], loader_version=game_config["loader_version"]
            )
        elif self.game_selected == "quilt":
            version = self.create_quilt_version(
                mc_version=game_config["mc_version"], loader_version=game_config["loader_version"]
            )
        elif self.game_selected == "forge":
            version = self.create_forge_version(
                mc_version=game_config["mc_version"], forge_version=game_config["forge_version"]
            )
        else:
            raise ValueError(f"Unknown valid game selected: {self.game_selected}")

        if autojoin:
            version.set_quick_play_multiplayer(self.server_ip)
        logger.debug("Version: %s", version)

        return version

    def provision_environment(
            self,
            version: Version | FabricVersion | ForgeVersion,
            auth_session: MicrosoftAuthSession,
            watcher: InstallWatcher=None
        )-> Environment:
        """
        Provisions an environment for the version to run.

        Parameters:
        - version (Version | FabricVersion | ForgeVersion): The version.
        - auth_session (MicrosoftAuthSession): The auth session to add to the version.
        - watcher (Watcher): The watcher for PortableMC. Defaults to None.

        Returns:
        - Environment: The environment for PortableMC.
        """
        logger.debug("version: %s", version)
        logger.debug("auth_session: %s", auth_session)
        logger.debug("watcher: %s", watcher)
        # force install of normal game files
        vanilla_mc_version = self.create_vanilla_version(
            self.remote_config["games"][self.game_selected]["mc_version"]
        )
        vanilla_mc_version.install(watcher=watcher)

        version.auth_session = auth_session
        env = version.install(watcher=watcher)
        args = SETTINGS.get_game("ram_jvm_args") + SETTINGS.get_game("additional_jvm_args")
        env.jvm_args.extend(args)
        return env

    def sync(self, app) -> Generator[tuple, None, None]:
        """
        Syncs the local data folder with the server.

        Parameters:
        - app: The app to update the GUI.
        """
        logger.debug("app: %s", app)

        app.update_title("Beginning Sync")
        app.progress_indeterminate()

        for remote_path in self.remote_config["paths"]:
            # Bool to determine if path is only for startup
            firstrun_only: bool = self.remote_config["paths"][remote_path]["first_start_only"]
            # Local path relative to data folder
            local_path_root: str = self.remote_config["paths"][remote_path]["root"]
            # Whether or not to overwrite existing files
            overwrite: bool = self.remote_config["paths"][remote_path]["overwrite_existing"]

            logger.debug("Firstrun Only: %s, Local Path Root: %s, Overwrite: %s",
                         firstrun_only, local_path_root, overwrite
            )

            if not SETTINGS.get_misc("first_start") and firstrun_only:
                logger.debug("Skipping '%s' because it is only for first start", remote_path)
                continue

            app.update_title(remote_path)
            app.reset_progress()

            # if its a file, download it
            if not remote_path.endswith("/"):
                app.update_item(f"Downloading: {remote_path}")

                file_url = remote.get_file_url(self.remote_tree, remote_path)
                if file_url is None:
                    logger.warning("'%s' not found on the server", remote_path)
                    continue

                # Local path relative to data folder
                local_path = self.context.work_dir / local_path_root

                # Form directory path
                local_path.parent.mkdir(parents=True, exist_ok=True)

                # Delete the file if it exists
                if overwrite and local_path.exists():
                    local_path.unlink()
                    logger.debug("Deleted existing file: %s", local_path)

                if not local_path.exists():
                    remote.download(file_url, local_path)
                    app.update_progress(1)
                else:
                    logger.debug("Skipping '%s' because it already exists", remote_path)
                continue

            # if its a directory, download all files and sub folders in it
            dir_paths = remote.get_dir_paths(self.remote_tree, remote_path)
            len_all_paths = len(dir_paths)
            if len_all_paths == 0:
                logger.warning("No files found in '%s'", remote_path)
                continue
            total_downloaded = 0
            for remote_path_item in dir_paths:
                app.update_item(f"Preparing: {remote_path_item[len(remote_path):]}")

                work_dir = self.context.work_dir
                root = work_dir / local_path_root
                root.mkdir(parents=True, exist_ok=True)
                file_url = remote.get_file_url(self.remote_tree, remote_path_item)
                if file_url is None:
                    logger.warning("'%s' not found on the server", remote_path_item)
                    continue

                # Local path relative to data folder
                local_path: Path = root / remote_path_item[len(remote_path):]

                # If there is no file extension, it is a directory
                if not local_path.suffix:
                    local_path.mkdir(parents=True, exist_ok=True)
                    logger.debug("Created directory: %s", local_path)
                    continue

                # Delete the file if it exists and is only for first start
                if overwrite and local_path.exists():
                    local_path.unlink()
                    logger.debug("Deleted existing file: %s", local_path)

                # FIXME: Invalid files are not being removed yet
                # FIXME: Zip files are corrupted (They cannot be raw base64)

                if not local_path.exists():
                    app.update_item(f"Downloading: {remote_path_item[len(remote_path):]}")
                    remote.download(file_url, local_path)
                    total_downloaded += 1
                    app.update_progress(total_downloaded / len_all_paths)
                else:
                    logger.debug("Skipping '%s' because it already exists", remote_path_item)
