"""
This module contains the LoginWindow class

Classes:
- LoginWindow: Represents the login window of the application.
"""

import customtkinter
from source.gui.auth_win import AuthWindow
from source.gui import utils

SETTINGS = utils.get_settings()


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
        self.geometry("450x200")
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)  # configure grid system

        # email label
        self.label = customtkinter.CTkLabel(
            self, text="Microsoft Email Address", font=SETTINGS.font_large
        )
        self.label.grid(row=0, column=0, pady=(20, 0))
        # email entry
        self.entry = customtkinter.CTkEntry(self, width=200)
        self.entry.grid(row=1, column=0, pady=(20, 0))
        self.entry.bind("<Return>", lambda _: self.login())
        # button
        self.button = customtkinter.CTkButton(
            self, text="Login", command=self.login, font=SETTINGS.font
        )
        self.button.grid(row=2, column=0, pady=(20, 0))

    def login(self):
        """
        Handles the login process.

        Disables the login button and creates an instance of the AuthWindow class
        to initiate the authentication process. Destroys the current login window.
        """
        self.button.configure(state="disabled")
        # create top level window
        self.auth_window = AuthWindow(master=self.master, email=self.entry.get())
        self.destroy()
