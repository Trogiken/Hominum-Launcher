"""
Contains the AuthWindow class.

Classes:
- AuthWindow: Window for authenticating the user.
"""

import logging
import threading
import customtkinter
from source import path, utils
from source.mc.authentication import AuthenticationHandler

logger = logging.getLogger(__name__)

class AuthWindow(customtkinter.CTkToplevel):
    """Window for authenticating the user."""
    def __init__(self, master, email, **kwargs):
        super().__init__(master, **kwargs)
        logger.debug("Creating authentication window")

        self.settings = utils.Settings()

        self.title("Authentication")
        self.email = email
        self.geometry("400x100")
        self.resizable(False, False)
        self.columnconfigure(0, weight=1)  # configure grid system

        # Make the window modal
        self.transient(master)  # Set to be a transient window of the master window
        self.grab_set()  # Direct all events to this window

        self.protocol("WM_DELETE_WINDOW", self.destroy)  # Handle the close event

        self.label = customtkinter.CTkLabel(
            self, text=f"Logging into {self.email}", font=self.settings.get_gui("font_large")
        )
        self.label.grid(row=0, column=0, pady=(20, 0))

        self.progress = customtkinter.CTkProgressBar(self, mode="indeterminate")
        self.progress.grid(row=1, column=0, pady=(20, 0))
        self.progress.start()

        auth_thread = threading.Thread(target=self.auth, daemon=True)
        auth_thread.start()

        logger.debug("Authentication window created")

        while auth_thread.is_alive():
            self.update_idletasks()
            self.update()

        self.destroy()
        logger.debug("Authentication window destroyed")

    def auth(self):
        """Runs the authentication process."""
        auth_handler = AuthenticationHandler(
            email=self.settings.get_user("email"), context=path.CONTEXT
        )
        auth_handler.authenticate()
