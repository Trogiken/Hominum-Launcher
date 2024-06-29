"""
This module contains the RunGameWindow class which is a custom tkinter window
that is used to run minecraft.

Classes:
- InstallWatcher: A class that watches the installation of the game.
- InstallFrame: A class that displays the installation progress accross operations.
- RunFrame: A class that displays the running progress of the game.
- RunGameWindow: A class that is used to run the game.
"""

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

SETTINGS = Settings()


class InstallWatcher(Watcher):
    """A class that watches the installation of the game."""
    def __init__(self, master):
        self.app = master
        self.total = 0

    def handle(self, event) -> None:
        """Handle the event."""
        if isinstance(event, DownloadStartEvent):
            self.app.update_title("Downloading Fabric MC")
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

    def start_installation(self):
        """
        Start the installation process.
        
        Returns:
        - None"""
        self.install_thread = threading.Thread(target=self.install)
        self.install_thread.start()
        self.check_thread()

    def check_thread(self):
        """
        Check if the thread is alive.
        If the thread is not alive, call the callback.
        """
        if self.install_thread.is_alive():
            # Check again after 100ms
            self.after(100, self.check_thread)
        else:
            # Thread is not alive, call the callback
            if self.errors_occurred:
                self.on_install_error()
                return
            if self.on_install_complete:
                self.on_install_complete()
                return

    def install(self):
        """
        Install the game and other necessary files.
        
        Returns:
        - None
        """
        # TODO: Handle errors such that the game wont start if the installation fails
        # Install the game
        install_watcher = InstallWatcher(self)
        for _ in range(3):  # Retry 3 times
            try:
                self.mc.provision_environment(self.version, watcher=install_watcher)
                self.errors_occurred = False
                break
            except Exception:
                # TODO: Log Errors
                self.errors_occurred = True

        # Prevent the next steps because the environment was not provisioned properly
        if self.errors_occurred:
            return

        # Sync Mods
        try:
            self.update_title("Syncing Mods")
            self.reset_progress()
            for count, total, filename in self.mc.sync_dir("mods"):
                self.update_item(filename)
                self.update_progress(count / total)
        except Exception:
            # TODO: Log Errors
            self.errors_occurred = True

        if SETTINGS.get_user("first_start"):
            # Sync Configurations
            try:
                self.update_title("Syncing Configurations")
                self.reset_progress()
                self.mc.sync_file("servers")
                self.mc.sync_file("options")
                for count, total, filename in self.mc.sync_dir("config"):
                    self.update_item(filename)
                    self.update_progress(count / total)
            except Exception:
                # TODO: Log Errors
                self.errors_occurred = True
            # Sync Resource Packs
            try:
                self.update_title("Syncing Resource Packs")
                self.reset_progress()
                for count, total, filename in self.mc.sync_dir("resourcepacks"):
                    self.update_item(filename)
                    self.update_progress(count / total)
            except Exception:
                # TODO: Log Errors
                self.errors_occurred = True
            # Sync Shader Packs
            try:
                self.update_title("Syncing Shader Packs")
                self.reset_progress()
                for count, total, filename in self.mc.sync_dir("shaderpacks"):
                    self.update_item(filename)
                    self.update_progress(count / total)
            except Exception:
                # TODO: Log Errors
                self.errors_occurred = True

        # Only set the user if no errors occurred
        if not self.errors_occurred:
            SETTINGS.set_user(first_start=False)

    def update_title(self, text):
        """Update the title label."""
        self.title_label.configure(text=text)

    def update_item(self, text):
        """Update the item label."""
        self.download_item_label.configure(text=text)

    def reset_progress(self):
        """Reset the progress bar."""
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(0)

    def update_progress(self, value):
        """Update the progress bar."""
        self.progress_bar.set(value)


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

    def run_game(self):
        """Start the game thread."""
        self.game_thread = threading.Thread(target=self.run)
        self.game_thread.start()
        self.check_thread()

    def check_thread(self):
        """
        Check if the thread is alive.
        If the thread is not alive, call the callback.
        """
        if self.game_thread.is_alive():
            # Check again after 100ms
            self.after(100, self.check_thread)
        else:
            # Thread is not alive, call the callback
            if self.on_run_complete:
                self.on_run_complete()

    def run(self):
        """Provision the environment and run the game."""
        env = self.mc.provision_environment(self.version)
        env.jvm_args.extend(SETTINGS.get_game("jvm_args"))
        if os.name != "posix":
            if not self.main_window.isMinimized:
                self.after(1000, self.main_window.minimize())
        env.run()


# TODO: If this window is destroyed, the game should be stopped
class RunGameWindow(customtkinter.CTkToplevel):
    """A class that is used to run the game."""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
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
        # TODO: Handle no auth
        if session is None:
            # TODO: Handle no auth
            return
        self.version.auth_session = session
        self.version.set_quick_play_multiplayer(self.mc.server_ip)

        # TODO: Maybe make this stop the game/installation
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

    def on_install_complete(self):
        """Destroy the install frame and create the run frame."""
        self.install_frame.destroy()
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

    def on_run_complete(self):
        """Close this window."""
        if os.name != "posix":
            if self.main_window.isMinimized:
                self.main_window.maximize()
                min_length, min_height = SETTINGS.get_gui("main_window_min_size")
                self.main_window.resizeTo(min_length, min_height)
        self.destroy()
