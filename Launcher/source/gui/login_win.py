"""
Contains the LoginWindow class.

Classes:
- LoginWindow: Window for entering login information.
"""

import logging
import customtkinter
from source import path, utils
from source.mc.authentication import AuthenticationHandler
from source.gui.auth_win import AuthWindow

logger = logging.getLogger(__name__)


class LoginWindow(customtkinter.CTkToplevel):
    """Window for entering login information."""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        logger.debug("Creating login window")

        self.settings = utils.Settings()

        self.title("Login")
        self.geometry("450x150")
        self.resizable(False, False)
        # Configure grid system for centering
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # email entry centered
        self.entry = customtkinter.CTkEntry(
            self,
            width=300,
            font=self.settings.get_gui("font_normal"),
            placeholder_text="Microsoft Email Address",
            justify="center",
        )
        self.entry.grid(row=1, column=1, pady=(20, 10), sticky="nsew")
        self.bind("<Return>", lambda _: self.login())

        # button centered
        self.button = customtkinter.CTkButton(
            self,
            width=150,
            text="Login",
            command=self.login,
            font=self.settings.get_gui("font_normal")
        )
        self.button.grid(row=2, column=1, pady=(10, 20))

        logger.debug("Login window created")

    def login(self):
        """
        Handles the login process.

        Disables the login button and creates an instance of the AuthWindow class
        to initiate the authentication process. Destroys the current login window.
        """
        self.button.configure(state="disabled")
        self.settings.set_user(email=self.entry.get())
        auth_handler = AuthenticationHandler(
            email=self.settings.get_user("email"), context=path.CONTEXT
        )
        self.auth_window = AuthWindow(master=self.master, email=self.entry.get())
        if not auth_handler.get_session():  # if the session failed, re-enable the button
            logger.error("Login session could not be established, releasing button")
            self.button.configure(state="normal")
        else:
            logger.debug("Login was successful")
            self.destroy()
            logger.debug("Login window destroyed")
