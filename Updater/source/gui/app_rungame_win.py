"""
This module contains the RunGameWindow class which is a custom tkinter window
that is used to run minecraft.

Classes:
- InstallWatcher: A class that watches the installation of the game.
- InstallFrame: A class that displays the installation progress accross operations.
- RunFrame: A class that displays the running progress of the game.
- RunGameWindow: A class that is used to run the game.
"""

import logging
import os
import threading
import customtkinter
from portablemc.standard import \
Watcher, DownloadCompleteEvent, DownloadProgressEvent, DownloadStartEvent
from portablemc.fabric import FabricVersion
from source.gui.popup_win import PopupWindow
from source import path
from source.utils import Settings
from source.mc.authentication import AuthenticationHandler
from source.mc import MCManager

if os.name != "posix":
    import pygetwindow as pygw

logger = logging.getLogger(__name__)

SETTINGS = Settings()


class InstallWatcher(Watcher):
    """A class that watches the installation of the game."""
    def __init__(self, master):
        self.app = master
        self.total = 0

    def handle(self, event) -> None:
        """Handle the event."""
        if isinstance(event, DownloadStartEvent):
            self.app.update_title("Provisioning Environment")
            self.app.reset_progress()
            self.total = event.entries_count
        elif isinstance(event, DownloadProgressEvent):
            self.app.update_item(event.entry)
            self.app.update_progress(event.count / self.total)
        elif isinstance(event, DownloadCompleteEvent):
            self.app.update_item("Download Complete")


class InstallFrame(customtkinter.CTkFrame):
    """A class that displays the installation progress accross operations."""
    def __init__(self,
                 master,
                 mc: MCManager,
                 version: FabricVersion,
                 on_install_complete=None,
                 on_install_error=None
        ):
        super().__init__(master)
        logger.debug("Creating install frame")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.mc = mc
        self.version = version
        self.on_install_complete = on_install_complete
        self.on_install_error = on_install_error
        self.errors_occurred = False

        # Title label
        self.title_label = customtkinter.CTkLabel(
            self, text="Please Wait", font=SETTINGS.get_gui("font_large")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 0))

        # Item Download Label
        self.download_item_label = customtkinter.CTkLabel(
            self, text="Getting things ready", font=SETTINGS.get_gui("font_normal")
        )
        self.download_item_label.grid(row=1, column=0, padx=20, pady=10)

        # Progress bar
        self.progress_bar = customtkinter.CTkProgressBar(self, mode="indeterminate")
        self.progress_bar.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")
        self.progress_bar.start()

        self.start_installation()

        logger.debug("Install frame created")

    def start_installation(self):
        """Start the installation process."""
        self.install_thread = threading.Thread(target=self._install)
        self.install_thread.start()
        self._check_thread()

    def _check_thread(self):
        """
        Check if the thread is alive.
        If the thread is not alive, call the callback.
        """
        if self.install_thread.is_alive():
            # Check again after 100ms
            self.after(100, self._check_thread)
        else:
            # Thread is not alive, call the callback
            if self.errors_occurred:
                self.on_install_error()
                return
            if self.on_install_complete:
                self.on_install_complete()
                return

    def _sync_items(self, item_name: str, remote_dir: str, is_dir: bool=True):
        """
        Sync the items of a specific type.
        
        Parameters:
        - item_name: The name of the item. Used for display and logging purposes.
        - remote_dir: The remote directory/file to sync.
        - is_dir: Whether the item is a directory or not. Set False if syncing one file
        """
        try:
            logger.info("Syncing %s", item_name.title())
            self.update_title(f"Syncing {item_name}")
            self.reset_progress()
            if is_dir:
                sync_iter = self.mc.sync_dir(remote_dir)
            else:
                self.mc.sync_file(remote_dir)
                sync_iter = []
            for count, total, filename, error_occured in sync_iter:
                self.update_item(filename)
                self.update_progress(count / total)
                if error_occured:
                    self.errors_occurred = True
            if self.errors_occurred:
                logger.warning("Some %s failed to sync", item_name.lower())
            else:
                logger.info("%s synced successfully", item_name.title())
        except Exception as sync_error:
            logger.error("Error syncing %s: %s", item_name.lower(), sync_error)
            self.errors_occurred = True

    def _install(self):
        """
        Install the game and other necessary files.
        
        Returns:
        - None
        """
        logger.info("Starting Installation")
        # Install the game
        install_watcher = InstallWatcher(self)
        for _ in range(3):  # Retry 3 times
            try:
                logger.info("Provisioning Environment")
                self.mc.provision_environment(self.version, watcher=install_watcher)
                self.errors_occurred = False
                logger.info("Environment provisioned successfully")
                break
            except Exception as env_error:
                logger.error("Error provisioning environment: %s", env_error)
                self.errors_occurred = True

        # Prevent the next steps because the environment was not provisioned properly
        if self.errors_occurred:
            logger.warning("Environment was not provisioned properly, stopping installation")
            return

        # Sync Mods
        self._sync_items("Mods", "mods")

        if SETTINGS.get_game("first_start"):
            # Sync Configurations
            self._sync_items("Configurations", "servers", is_dir=False)
            self._sync_items("Configurations", "options", is_dir=False)
            self._sync_items("Configurations", "config")

            # Sync Resource Packs
            self._sync_items("Resource Packs", "resourcepacks")

            # Sync Shader Packs
            self._sync_items("Shader Packs", "shaderpacks")

        # Only set the user if no errors occurred
        if not self.errors_occurred:
            SETTINGS.set_game(first_start=False)
            logger.info("Installation finished successfully")
        else:
            logger.warning("Installation finished with errors")

    def update_title(self, text):
        """Update the title label."""
        self.title_label.configure(text=text)
        logger.debug("Title set to '%s'", text)

    def update_item(self, text):
        """Update the item label."""
        self.download_item_label.configure(text=text)
        logger.debug("Item set to '%s'", text)

    def reset_progress(self):
        """Reset the progress bar."""
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(0)
        logger.debug("Progress bar reset")

    def update_progress(self, value):
        """Update the progress bar."""
        self.progress_bar.set(value)
        logger.debug("Progress set to '%s'", value)


class RunFrame(customtkinter.CTkFrame):
    """A class that displays the running progress of the game."""
    def __init__(
            self,
            master,
            mc: MCManager,
            version: FabricVersion,
            on_run_complete=None,
            main_window=None
        ):
        super().__init__(master)
        logger.debug("Creating run frame")

        self.grid_columnconfigure(0, weight=1)

        self.mc = mc
        self.version = version
        self.on_run_complete = on_run_complete
        self.main_window = main_window

        self.title_label = customtkinter.CTkLabel(
            self, text="Game Running", font=SETTINGS.get_gui("font_large")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=20)

        self.message_label = customtkinter.CTkLabel(
            self,
            text="Please wait until the Minecraft window opens",
            font=SETTINGS.get_gui("font_normal")
        )
        self.message_label.grid(row=1, column=0, padx=20, pady=(0, 20))

        self.run_game()

        logger.debug("Run frame created")

    def run_game(self):
        """Start the game thread."""
        self.game_thread = threading.Thread(target=self.run)
        self.game_thread.start()
        self._check_thread()

    def _check_thread(self):
        """
        Check if the thread is alive.
        If the thread is not alive, call the callback.
        """
        if self.game_thread.is_alive():
            # Check again after 100ms
            self.after(100, self._check_thread)
        else:
            # Thread is not alive, call the callback
            if self.on_run_complete:
                self.on_run_complete()

    def run(self):
        """Provision the environment and run the game."""
        logger.info("Running game")
        env = self.mc.provision_environment(self.version)
        args = SETTINGS.get_game("ram_jvm_args") + SETTINGS.get_game("additional_jvm_args")
        logger.debug("Runtime args: %s", args)
        env.jvm_args.extend(args)
        if os.name != "posix":
            if not self.main_window.isMinimized:
                self.after(1000, self.main_window.minimize())
                logger.debug("Main window minimized")
        env.run()


class RunGameWindow(customtkinter.CTkToplevel):
    """A class that is used to run the game."""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        logger.debug("Creating run game window")

        self.title("Run Game")  # Set self.this_window also when changed!
        # Used to minimize the window after the game starts
        self.main_window = None
        if os.name != "posix":
            self.main_window: pygw.Win32Window = pygw.getWindowsWithTitle("Hominum")[0]
        self.mc = MCManager(context=path.CONTEXT)
        self.auth_handler = AuthenticationHandler(
            email=SETTINGS.get_user("email"), context=path.CONTEXT
        )
        self.version = self.mc.provision_version(self.mc.fabric_version, self.mc.loader_version)
        session = self.auth_handler.get_session()
        if session is None:
            PopupWindow(
                self,
                title="Authentication Error",
                message="No authentication session found. Please login."
            )
            self.after(100, self.destroy)
            return
        self.version.auth_session = session
        if SETTINGS.get_game("autojoin") and self.mc.server_ip:
            self.version.set_quick_play_multiplayer(self.mc.server_ip)
            logger.debug("Auto-join set to '%s'", self.mc.server_ip)

        self.protocol("WM_DELETE_WINDOW", lambda: None)  # Prevent the closing of this window

        self.attributes("-topmost", True)  # Always on top
        self.geometry("500x150")
        self.resizable(False, False)
        self.columnconfigure(0, weight=1)  # configure grid system
        self.rowconfigure(0, weight=1)

        # create install frame
        self.install_frame = InstallFrame(
            self,
            self.mc,
            self.version,
            on_install_complete=self.on_install_complete,
            on_install_error=self.on_install_error
        )
        self.install_frame.grid(row=0, column=0, sticky="nsew")

        logger.debug("Created run game window")

    def on_install_complete(self):
        """Destroy the install frame and create the run frame."""
        self.install_frame.destroy()
        logger.debug("Install frame destroyed")
        run_frame = RunFrame(
            self,
            self.mc,
            self.version,
            on_run_complete=self.on_run_complete,
            main_window=self.main_window
        )
        run_frame.grid(row=0, column=0, sticky="nsew")

    def on_install_error(self):
        """Display an error message."""
        PopupWindow(
            self,
            title="Error",
            message="An error occurred during the installation process",
        )
        self.destroy()
        logger.debug("Popup destroyed")

    def on_run_complete(self):
        """Close this window."""
        logger.info("Game stopped")
        if os.name != "posix":
            if self.main_window.isMinimized:
                self.main_window.maximize()
                logger.debug("Main window maximized")
                min_length, min_height = SETTINGS.get_gui("main_window_min_size")
                self.main_window.resizeTo(min_length, min_height)
                logger.debug("Main window resized to '%s'x'%s'", min_length, min_height)
        self.destroy()
        logger.debug("Run game window destroyed")
