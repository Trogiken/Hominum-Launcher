"""
The install window is a window that displays the installation progress across operations.

classes:
- InstallWindow: A class that displays the installation progress across operations.
"""

import logging
import customtkinter
from source.gui.popup_win import PopupWindow
from source import path, exceptions
from source import utils
from source.mc.authentication import AuthenticationHandler
from source.mc import MCManager
from source.mc.minecraft import InstallWatcher

logger = logging.getLogger(__name__)

SETTINGS = utils.Settings()


class InstallWindow(customtkinter.CTkToplevel):
    """A class that displays the installation progress accross operations."""
    def __init__(self):
        super().__init__()
        logger.debug("Creating install window")

        self.title("Install")
        self.attributes("-topmost", True)  # Always on top
        self.geometry("500x150")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.mc = MCManager(context=path.CONTEXT)
        self.auth_handler = AuthenticationHandler(
            email=SETTINGS.get_user("email"), context=path.CONTEXT
        )
        try:
            self.version = self.mc.provision_version(autojoin=SETTINGS.get_game("autojoin"))
        except Exception as version_error:
            logger.error("Error getting version: %s", version_error)
            PopupWindow(
                self,
                title="Version Error",
                message="An error occurred while getting the version. Please try again.",
            )
            self.after(100, self.destroy)

        self.environment = None
        self.errors_occurred = False

        self.session = self.auth_handler.get_session()
        if self.session is None:
            logger.warning("No authentication session found during installation")
            PopupWindow(
                self,
                title="Authentication Error",
                message="No authentication session found. Please login."
            )
            self.after(100, self.destroy)

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

        self.after(100, self._install)

        logger.debug("Install window created")

    def _install(self):
        """
        Install the game and other necessary files.
        
        Returns:
        - None
        """
        logger.info("Starting Installation")
        # Install the game
        install_watcher = InstallWatcher(self)
        if SETTINGS.get_game("environment"):  # Reset environment if one exists
            SETTINGS.set_game(environment=utils.GameSettings().environment)
        for _ in range(3):  # Retry 3 times
            try:
                logger.info("Provisioning Environment")
                self.environment = self.mc.provision_environment(
                    version=self.version,
                    auth_session=self.session,
                    watcher=install_watcher,
                )
                self.errors_occurred = False
                logger.info("Environment provisioned successfully")
                break
            except Exception as env_error:
                if isinstance(env_error, exceptions.GlobalKill):
                    self.errors_occurred = True
                    return
                logger.error("Error provisioning environment: %s", env_error)
                self.errors_occurred = True

        # Prevent the next steps because the environment was not provisioned properly
        if self.errors_occurred:
            logger.warning("Environment was not provisioned properly, stopping installation")
        else:
            try:
                self.mc.sync(self)
            except Exception as sync_error:
                logger.error("Error syncing files: %s", sync_error)
                self.errors_occurred = True

        # Only set the user if no errors occurred
        if not self.errors_occurred:
            SETTINGS.set_misc(first_start=False)
            SETTINGS.set_game(environment=self.environment)
            logger.info("Installation finished successfully")
        else:
            logger.warning("Installation finished with errors")
            PopupWindow(
                self,
                title="Install Error",
                message="An error occurred during the installation process",
            )
        self.destroy()

    def update_gui(self):
        """Update the GUI."""
        self.update()
        self.update_idletasks()

    def update_title(self, text):
        """Update the title label."""
        self.title_label.configure(text=text)
        logger.debug("Title set to '%s'", text)
        self.update_gui()

    def update_item(self, text):
        """Update the item label."""
        self.download_item_label.configure(text=text)
        logger.debug("Item set to '%s'", text)
        self.update_gui()

    def reset_progress(self):
        """Reset the progress bar."""
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(0)
        logger.debug("Progress bar reset")
        self.update_gui()

    def progress_indeterminate(self):
        """Sets the progress bar to be indeterminate"""
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()
        self.update_gui()

    def update_progress(self, value):
        """Update the progress bar."""
        self.progress_bar.set(value)
        logger.debug("Progress set to '%s'", value)
        self.update_gui()
