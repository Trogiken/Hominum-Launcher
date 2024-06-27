"""
This module contains the LoginWindow class

Classes:
- LoginWindow: Represents the login window of the application.
"""

import customtkinter
from source.mc import AuthenticationHandler
from source.gui.auth_win import AuthWindow
from source.utils import Settings
from source import path

SETTINGS = Settings()


class LoginWindow(customtkinter.CTkToplevel):
    """
    Represents the login window of the application.

    Methods:
        __init__: Initializes the LoginWindow instance.
        login: Handles the login process.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
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
            font=SETTINGS.get_gui("font_normal"),
            placeholder_text="Microsoft Email Address",
            justify="center",
        )
        self.entry.grid(row=1, column=1, pady=(20, 10), sticky="nsew")
        self.bind("<Return>", lambda _: self.login())

        # button centered
        self.button = customtkinter.CTkButton(
            self, width=150, text="Login", command=self.login, font=SETTINGS.get_gui("font_normal")
        )
        self.button.grid(row=2, column=1, pady=(10, 20))

    def login(self):
        """
        Handles the login process.

        Disables the login button and creates an instance of the AuthWindow class
        to initiate the authentication process. Destroys the current login window.
        """
        self.button.configure(state="disabled")
        SETTINGS.set_user(email=self.entry.get())
        auth_handler = AuthenticationHandler(email=SETTINGS.get_user("email"), context=path.CONTEXT)
        self.auth_window = AuthWindow(master=self.master, email=self.entry.get())
        if not auth_handler.refresh_session():  # if the session failed, re-enable the button
            # TODO: Log this as an error
            self.button.configure(state="normal")
        else:
            self.destroy()
