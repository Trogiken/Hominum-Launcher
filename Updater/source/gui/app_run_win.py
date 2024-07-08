import os
import logging
import threading
import customtkinter
from portablemc.standard import Version, Environment
from portablemc.fabric import FabricVersion
from portablemc.forge import ForgeVersion
from source.mc import MCManager
from source import utils


# FIXME: Reimplement (Minimizing, threading, etc)

if os.name != "posix":
    import pygetwindow as pygw

logger = logging.getLogger(__name__)

SETTINGS = utils.Settings()


class RunFrame(customtkinter.CTkFrame):
    """A class that displays the running progress of the game."""
    def __init__(
            self,
            master,
            mc: MCManager,
            version: Version | FabricVersion | ForgeVersion,
            environment: Environment,
            on_run_complete=None,
            main_window=None
        ):
        super().__init__(master)
        logger.debug("Creating run frame")

        master.protocol("WM_DELETE_WINDOW", lambda: None)  # Prevent the closing of this window

        self.grid_columnconfigure(0, weight=1)

        self.mc = mc
        self.version = version
        self.environment = environment
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
        env = self.environment
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
        session = self.auth_handler.get_session()
        if session is None:
            PopupWindow(
                self,
                title="Authentication Error",
                message="No authentication session found. Please login."
            )
            self.after(100, self.destroy)
            return
        self.version = self.mc.provision_version(
            auth_session=session, autojoin=SETTINGS.get_game("autojoin")
        )

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

    def on_install_complete(self, environment: Environment):
        """Destroy the install frame and create the run frame."""
        self.install_frame.destroy()
        logger.debug("Install frame destroyed")
        run_frame = RunFrame(
            self,
            self.mc,
            self.version,
            environment,
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
        logger.debug("Run game window destroyed")

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
