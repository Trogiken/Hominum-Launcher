"""
This module contains the main window of the application.

classes:
- LeftFrame: Contains a settings icon and functions.
- RightFrame: Contains user account info and logout button.
- CenterFrame: Contains tabs for whitelisting and syncing mods.
- App: The main window of the application.
"""

import customtkinter
from source.mc import MCManager
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
        self.login_window = None
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # User Dropdown
        if SETTINGS.get_user("email"):
            self.auth_handler = AuthenticationHandler(
                email=SETTINGS.get_user("email"), context=path.CONTEXT
            )
            username = self.auth_handler.get_username()
            if username:
                self.user_menu_var = customtkinter.StringVar(value=username)
                user_menu_values = ["Logout"]
            else:
                self.user_menu_var = customtkinter.StringVar(value="Logged Out")
                user_menu_values = ["Login"]
        else:
            self.user_menu_var = customtkinter.StringVar(value="Logged Out")
            user_menu_values = ["Login"]
        self.user_menu = customtkinter.CTkOptionMenu(
            self,
            font=SETTINGS.get_gui("font_normal"),
            values=user_menu_values,
            command=self.user_menu_callback,
            variable=self.user_menu_var
        )
        self.user_menu.grid(row=0, column=0, padx=20, pady=20, sticky="n")

        self.play_button_photo = customtkinter.CTkImage(
            get_image("play.png").resize(SETTINGS.get_gui("image_large"))
        )
        self.play_button = customtkinter.CTkButton(
            self,
            image=self.play_button_photo,
            text="Play",
            font=SETTINGS.get_gui("font_large"),
            fg_color="green",
            command=self.run_game
        )
        self.play_button.grid(row=0, column=0, padx=20, pady=20, sticky="s")

    def user_menu_callback(self, action: str):
        """
        Callback function for the user menu.

        Parameters:
        - action (str): The action to perform.

        Returns:
        - None
        """
        action = action.casefold()
        if action == "logout":
            auth_handler = AuthenticationHandler(SETTINGS.get_user("email"), path.CONTEXT)
            auth_handler.remove_session()
            self.user_menu_var.set("Logged Out")
            self.user_menu.configure(values=["Login"])
            self.user_menu_var.set("Login")
        if action == "login":
            if self.login_window is not None and self.login_window.winfo_exists():
                self.login_window.lift()
            else:
                self.login_window = LoginWindow(master=self)
                self.login_window.transient(self)
                self.wait_window(self.login_window)
                auth_handler = AuthenticationHandler(SETTINGS.get_user("email"), path.CONTEXT)
                username = auth_handler.get_username()
                if username:
                    self.user_menu_var.set(username)
                    self.user_menu.configure(values=["Logout"])
                else:
                    self.user_menu_var.set("Logged Out")
                    self.user_menu.configure(values=["Login"])

    def run_game(self):
        """Start Minecraft"""
        self.play_button.configure(state="disabled")

        run_window = RunGameWindow(master=self.master)
        self.wait_window(run_window)

        self.play_button.configure(state="normal")


class ScrollableFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master)
        self.mc = MCManager(context=path.CONTEXT)

        # Parse the bulletin config and create the bulletin
        bulletin_config: dict = self.mc.remote_config.get("bulletin", None)
        if not bulletin_config:
            self.columnconfigure(0, weight=1)
            self.rowconfigure(0, weight=1)
            # Create a frame that will center the label
            centering_frame = customtkinter.CTkFrame(self)
            centering_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(0, weight=1)
            # Now, centering_frame will expand to fill the ScrollableFrame

            # Place the no_bulletin_label in the centering_frame
            no_bulletin_label = customtkinter.CTkLabel(
                centering_frame, text="No Bulletin Available", font=SETTINGS.get_gui("font_large")
            )
            no_bulletin_label.place(relx=0.5, rely=0.5, anchor="center")
            return

        for column in bulletin_config.keys():
            column_number = int(column.split("_")[1])
            self.columnconfigure(
                column_number, weight=1, uniform="column_group"  # Change size together
            )
            # Below this line is management within the frames themselves
            section_row = 0
            for section, items in bulletin_config[column].items():
                section_frame = customtkinter.CTkFrame(self)
                section_frame.grid(
                    row=section_row, column=column_number, padx=10, pady=10, sticky="nsew"
                )
                section_frame.grid_columnconfigure(0, weight=1)
                section_label = customtkinter.CTkLabel(
                    section_frame, text=section, font=SETTINGS.get_gui("font_large")
                )
                section_label.grid(row=section_row, column=0, padx=10, pady=10, sticky="n")
                section_row += 1
                item_row = section_row
                for i, item in enumerate(items):
                    pady = (10, 0) if i < len(items) - 1 else 10  # Add padding to the last item
                    item_label = customtkinter.CTkLabel(
                        section_frame, text=item, font=SETTINGS.get_gui("font_normal")
                    )
                    item_label.grid(row=item_row, column=0, padx=10, pady=pady, sticky="w")
                    item_row += 1


class CenterFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=2)

        # Title Label
        self.title_label = customtkinter.CTkLabel(
            self, text="Server Bulletin", font=SETTINGS.get_gui("font_large")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="n")

        # Scrollable Frame
        self.scrollable_frame = ScrollableFrame(self)
        self.scrollable_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")


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

        self.settings_frame = LeftFrame(self)
        self.settings_frame.grid(row=0, column=0, padx=(10, 0), pady=10, sticky="nsw")

        self.right_frame = RightFrame(self)
        self.right_frame.grid(row=0, column=2, padx=(0, 10), pady=10, sticky="nse")

        self.center_frame = CenterFrame(self)
        self.center_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
