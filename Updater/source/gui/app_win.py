"""
Main window of the application.

classes:
- App: The main window of the application.
"""

import customtkinter
from source import path
from source.gui.login_win import LoginWindow
from source.gui import utils

SETTINGS = utils.get_settings()


class LeftFrame(customtkinter.CTkFrame):
    """This frame contains a settings icon and functions."""
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Title
        self.title_label = customtkinter.CTkLabel(
            self, text=path.PROGRAM_NAME_LONG, font=SETTINGS.font_large
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="n")

        # Version
        self.version_label = customtkinter.CTkLabel(
            self, text=f"v{path.VERSION}", font=SETTINGS.font_small
        )
        self.version_label.grid(row=1, column=0, padx=24, pady=0, sticky="sw")

        # Settings Button
        self.settings_button_photo = customtkinter.CTkImage(
            utils.get_image("settings.png").resize(SETTINGS.image_normal)
        )
        self.settings_button = customtkinter.CTkButton(
            self,
            image=self.settings_button_photo,
            text="Settings",
            font=SETTINGS.font_normal,
            command=self.open_settings
        )
        self.settings_button.grid(row=2, column=0, padx=20, pady=20, sticky="s")

    def open_settings(self):
        "TEST"
        print("settings")


class RightFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)


class CenterFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)


class App(customtkinter.CTk):
    """The main window of the application."""
    def __init__(self):
        super().__init__()
        self.title(path.PROGRAM_NAME)
        self.geometry("1000x400")
        self.minsize(1000, 400)
        self.grid_rowconfigure(0, weight=1)  # configure grid system
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)

        # TODO: if not logged in show login window and wait for login
        self.login_window = LoginWindow(master=self)
        self.login_window.transient(self)
        self.wait_window(self.login_window)

        # TODO: if logged in show main window, else show error message and repeat login
        self.focus_force()
        self.settings_frame = LeftFrame(self)
        self.settings_frame.grid(row=0, column=0, padx=(10, 0), pady=10, sticky="nsw")

        self.right_frame = RightFrame(self)
        self.right_frame.grid(row=0, column=2, padx=(0, 10), pady=10, sticky="nse")

        self.center_frame = CenterFrame(self)
        self.center_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
