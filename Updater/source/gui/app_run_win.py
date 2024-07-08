import os
import logging
import threading
import customtkinter
from portablemc.standard import Environment
from source.gui.popup_win import PopupWindow
from source import utils

if os.name != "posix":
    import pygetwindow as pygw

logger = logging.getLogger(__name__)

SETTINGS = utils.Settings()


class RunWindow(customtkinter.CTkToplevel):
    """A class that is used to run the game."""
    def __init__(self):
        super().__init__()
        logger.debug("Creating game window")

        self.title("Run")
        # Used to minimize the main window after the game starts
        self.main_window = None
        if os.name != "posix":
            self.main_window: pygw.Win32Window = pygw.getWindowsWithTitle("Hominum")[0]

        self.protocol("WM_DELETE_WINDOW", lambda: None)  # Prevent the closing of this window
        self.attributes("-topmost", True)  # Always on top
        self.geometry("500x150")
        self.resizable(False, False)
        self.columnconfigure(0, weight=1)  # configure grid system

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

        logger.debug("Created game window")

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
            # Check again after 1000ms
            self.after(1000, self.check_thread)
        else:
            # Thread is not alive, call the callback
            self.on_run_complete()

    def run(self):
        """Provision the environment and run the game."""
        logger.info("Running game")
        env: Environment = SETTINGS.get_game("environment")
        if env is None:
            PopupWindow(
                self,
                title="No Environment",
                message="Environment could not be found in settings. "\
                "Make sure the installation completed successfully."
            )
            return

        if os.name != "posix" and self.main_window:
            if not self.main_window.isMinimized:
                self.after(1000, self.main_window.minimize())
                logger.debug("Main window minimized")
        env.run()

    def on_run_complete(self):
        """Close this window."""
        logger.info("Game stopped")
        SETTINGS.set_game(environment=utils.GameSettings().environment)  # Reset the environment
        if os.name != "posix" and self.main_window:
            if self.main_window.isMinimized:
                self.main_window.maximize()
                logger.debug("Main window maximized")
                min_length, min_height = SETTINGS.get_gui("main_window_min_size")
                self.main_window.resizeTo(min_length, min_height)
                logger.debug("Main window resized to '%s'x'%s'", min_length, min_height)
        self.destroy()
        logger.debug("Run game window destroyed")
