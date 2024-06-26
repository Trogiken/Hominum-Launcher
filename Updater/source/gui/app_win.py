"""
This module contains the main window of the application.

classes:
- LeftFrame: Contains a settings icon and functions.
- RightFrame: Contains user account info and logout button.
- CenterFrame: Contains tabs for whitelisting and syncing mods.
- App: The main window of the application.
"""

import customtkinter
import pygetwindow
from source.mc.authentication import AuthenticationHandler
from source import path
from source.gui.login_win import LoginWindow
from source.gui.app_settings_win import SettingsWindow
from source.gui.app_rungame_win import RunGameWindow
from source.utils import Settings, get_image
SETTINGS = Settings()


class LeftFrame(customtkinter.CTkFrame):
    """This frame contains a settings icon and functions."""
    def __init__(self, master):
        super().__init__(master)
        self.settings_window = None
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Title
        self.title_label = customtkinter.CTkLabel(
            self, text=path.PROGRAM_NAME_LONG, font=SETTINGS.get_gui("font_large")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="n")

        # Version
        self.version_label = customtkinter.CTkLabel(
            self, text=f"v{path.VERSION}", font=SETTINGS.get_gui("font_small")
        )
        self.version_label.grid(row=1, column=0, padx=24, pady=0, sticky="sw")

        # Theme Drop Down
        self.theme_menu_var = customtkinter.StringVar(value=SETTINGS.get_gui("appearance").title())
        self.theme_menu = customtkinter.CTkOptionMenu(
            self,
            values=["System", "Dark", "Light"],
            font=SETTINGS.get_gui("font_normal"),
            command=self.theme_menu_callback,
            variable=self.theme_menu_var
        )
        self.theme_menu.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="s")

        # Settings Button
        self.settings_button_photo = customtkinter.CTkImage(
            get_image("settings.png").resize(SETTINGS.get_gui("image_normal"))
        )
        self.settings_button = customtkinter.CTkButton(
            self,
            image=self.settings_button_photo,
            text="Settings",
            font=SETTINGS.get_gui("font_normal"),
            command=self.open_settings
        )
        self.settings_button.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="s")

    def theme_menu_callback(self, theme: str):
        """
        Changes and saves the current program appearance
        
        Parmeters:
        - theme (str): Theme to set.

        Returns:
        - None
        """
        new_theme = theme.casefold()
        SETTINGS.set_gui(appearance=new_theme)
        customtkinter.set_appearance_mode(new_theme)

    def open_settings(self):
        """Opens the settings window."""
        # check if settings window already exists
        if self.settings_window is not None and self.settings_window.winfo_exists():
            # If the settings window exists and is open, bring it to the front
            self.settings_window.lift()
        else:
            # Otherwise, create a new settings window
            self.settings_window = SettingsWindow(master=self.master)
            self.settings_window.transient(self)
            self.wait_window(self.settings_window)
            self.settings_window = None  # Reset the attribute when the window is closed


class RightFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        # TODO: Display User account info and logout button


class CenterFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        # TODO: Add tabs, one for whitelisting, one for syncing mods. Add a frame to each tab for the content
        self.play_button_photo = customtkinter.CTkImage(
            get_image("play.png").resize(SETTINGS.get_gui("image_large"))
        )
        self.play_button = customtkinter.CTkButton(
            self,
            image=self.play_button_photo,
            text="Play",
            font=SETTINGS.get_gui("font_large"),
            command=self.run_game
        )
        self.play_button.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    def run_game(self):
        """Start Minecraft"""
        self.play_button.configure(state="disabled")
        window: pygetwindow.Win32Window = pygetwindow.getWindowsWithTitle("Hominum")[0]
        window.minimize(window)

        run_window = RunGameWindow(master=self.master)
        run_window.transient(self)
        self.wait_window(run_window)

        self.play_button.configure(state="normal")
        window.maximize()
        window.resizeTo(1000, 400)
        window.moveTo(0, 0)


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

        # Load settings
        customtkinter.set_appearance_mode(SETTINGS.get_gui("appearance"))

        auth_handler = AuthenticationHandler(email=SETTINGS.get_user("email"), context=path.CONTEXT)
        session = auth_handler.refresh_session()
        if session is None:
            self.login_window = LoginWindow(master=self)
            self.login_window.transient(self)
            self.wait_window(self.login_window)

        self.settings_frame = LeftFrame(self)
        self.settings_frame.grid(row=0, column=0, padx=(10, 0), pady=10, sticky="nsw")

        self.right_frame = RightFrame(self)
        self.right_frame.grid(row=0, column=2, padx=(0, 10), pady=10, sticky="nse")

        self.center_frame = CenterFrame(self)
        self.center_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

