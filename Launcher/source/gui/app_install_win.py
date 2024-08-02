"""
Contains the InstallWindow class.

classes:
- InstallWindow: A class that displays the installation progress across operations.
"""

import logging
import customtkinter
from source.gui.popup_win import PopupWindow
from source import utils, path, exceptions
from source.mc.authentication import AuthenticationHandler
from source.mc.minecraft import MCManager, InstallWatcher

logger = logging.getLogger(__name__)


class InstallWindow(customtkinter.CTkToplevel):
    """A class that displays the installation progress accross operations."""
    def __init__(self):
        super().__init__()
        logger.debug("Creating install window")

        self.settings = utils.Settings()

        self.title("Install")
        self.attributes("-topmost", True)  # Always on top
        self.geometry("500x150")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.mc = MCManager(context=path.CONTEXT)
        self.auth_handler = AuthenticationHandler(
            email=self.settings.get_user("email"), context=path.CONTEXT
        )
        try:
            self.version = self.mc.provision_version(autojoin=self.settings.get_game("autojoin"))
        except Exception as version_error:
            logger.error("Error getting version: %s", version_error)
            version_popup_window = PopupWindow(
                self,
                title="Version Error",
                message="An error occurred while getting the version. Please try again.",
            )
            version_popup_window.wait_window()
            self.version = None

        self.environment = None
        self.errors_occurred = False

        self.session = self.auth_handler.get_session()
        if self.session is None:
            logger.warning("No authentication session found during installation")
            auth_popup_window = PopupWindow(
                self,
                title="Authentication Error",
                message="No authentication session found. Please login."
            )
            auth_popup_window.wait_window()
            self.session = None

        # Title label
        self.title_label = customtkinter.CTkLabel(
            self, text="Please Wait", font=self.settings.get_gui("font_large")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 0))

        # Item Download Label
        self.download_item_label = customtkinter.CTkLabel(
            self, text="Getting things ready", font=self.settings.get_gui("font_normal")
        )
        self.download_item_label.grid(row=1, column=0, padx=20, pady=10)

        # Progress bar
        self.progress_bar = customtkinter.CTkProgressBar(self, mode="indeterminate")
        self.progress_bar.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")
        self.progress_bar.start()

        if self.version and self.session:
            self.after(100, self.install)
        else:
            self.after(100, self.destroy)

        logger.debug("Install window created")

    def install(self):
        """Install the game and other necessary files."""
        logger.info("Starting Installation")
        version_environment = None
        # Install the game
        install_watcher = InstallWatcher(self)
        for _ in range(3):  # Retry 3 times
            try:
                logger.info("Provisioning Environment")
                version_environment = self.mc.provision_environment(
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
                sync_thread = utils.PropagatingThread(target=self.mc.sync, args=(self,))
                sync_thread.start()

                while sync_thread.is_alive():
                    self.update_gui()
                sync_thread.join()
            except Exception as sync_error:
                logger.error("Error syncing files: %s", sync_error)
                self.errors_occurred = True

        if not version_environment:
            logger.warning("Environment is not set")

        # Only set the user if no errors occurred
        if not self.errors_occurred and version_environment:
            self.environment = version_environment
            logger.info("Installation finished successfully")
        else:
            logger.warning("Installation finished with errors")
            install_error_popup = PopupWindow(
                self,
                title="Install Error",
                message="An error occurred during the installation process",
            )
            install_error_popup.wait_window()
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
