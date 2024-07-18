"""
This module contains the main window of the application.

classes:
- LeftFrame: Contains the settings icon and functions.
- RightFrame: Contains the user dropdown and functions.
- ScrollableFrame: Contains the bulletin.
- CenterFrame: Contains the bulletin.
- App: The main window of the application.
"""

from time import sleep
import logging
import os
import importlib.util
import customtkinter
from source.mc import MCManager
from source.mc.authentication import AuthenticationHandler
from source import path
from source.gui.login_win import LoginWindow
from source.gui.app_settings_win import SettingsWindow
from source.gui.app_install_win import InstallWindow
from source.gui.app_run_win import RunWindow
from source  import utils

if '_PYIBoot_SPLASH' in os.environ and importlib.util.find_spec("pyi_splash"):
    try:
        import pyi_splash  # type: ignore
        SPLASH_FOUND = True
    except ImportError:
        SPLASH_FOUND = False
else:
    SPLASH_FOUND = False

logger = logging.getLogger(__name__)

SETTINGS = utils.Settings()


class LeftFrame(customtkinter.CTkFrame):
    """This frame contains a settings icon and functions."""
    def __init__(self, master):
        super().__init__(master)
        logger.debug("Creating left frame")

        self.settings_window = None
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Title
        self.title_label = customtkinter.CTkLabel(
            self, text=path.PROGRAM_NAME_LONG, font=SETTINGS.get_gui("font_title")
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
            utils.get_image("settings.png").resize(SETTINGS.get_gui("image_normal"))
        )
        self.settings_button = customtkinter.CTkButton(
            self,
            image=self.settings_button_photo,
            text="Settings",
            font=SETTINGS.get_gui("font_normal"),
            command=self.open_settings
        )
        self.settings_button.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="s")

        logger.debug("Left frame created")

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
    """This frame contains the user dropdown and functions."""
    def __init__(self, master, mcmanager: MCManager=None):
        super().__init__(master)
        logger.debug("Creating right frame")

        if mcmanager is None:
            raise ValueError("MCManager object is required")

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
                altnames: dict = mcmanager.remote_config.get("altnames", {})
                if username in altnames:
                    username = altnames[username]
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

        # Auto-Join Switch
        self.autojoin_switch_var = customtkinter.BooleanVar(value=SETTINGS.get_game("autojoin"))
        self.autojoin_switch = customtkinter.CTkSwitch(
            self,
            text="Auto-Join",
            font=SETTINGS.get_gui("font_normal"),
            command=self.auto_join_callback,
            variable=self.autojoin_switch_var,
            onvalue=True,
            offvalue=False
        )
        self.autojoin_switch.grid(row=1, column=0, padx=20, pady=0, sticky="s")

        self.play_button_photo = customtkinter.CTkImage(
            utils.get_image("rocket.png").resize(SETTINGS.get_gui("image_large"))
        )
        self.play_button = customtkinter.CTkButton(
            self,
            image=self.play_button_photo,
            text="Play",
            font=SETTINGS.get_gui("font_title"),
            fg_color="green",
            command=self.run_game
        )
        self.play_button.grid(row=2, column=0, padx=20, pady=20, sticky="s")

        logger.debug("Right frame created")

    def auto_join_callback(self):
        """
        Callback function for the auto-join switch.

        Returns:
        - None
        """
        action = self.autojoin_switch_var.get()
        if action is True:
            self.autojoin_switch_var.set(True)
            SETTINGS.set_game(autojoin=True)
        elif action is False:
            self.autojoin_switch_var.set(False)
            SETTINGS.set_game(autojoin=False)

    def user_menu_callback(self, action: str):
        """
        Callback function for the user menu.

        Parameters:
        - action (str): The action to perform.

        Returns:
        - None
        """
        action = action.casefold()
        logger.debug("User menu callback action: %s", action)
        if action == "logout":
            auth_handler = AuthenticationHandler(SETTINGS.get_user("email"), path.CONTEXT)
            auth_handler.remove_session()
            self.user_menu_var.set("Logged Out")
            self.user_menu.configure(values=["Login"])
            self.user_menu_var.set("Login")
            logger.debug("Logout complete")
        if action == "login":
            if self.login_window is not None and self.login_window.winfo_exists():
                self.login_window.lift()
                logger.debug("Login window already exists")
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
                self.login_window = None
                logger.debug("Login complete")


    def run_game(self):
        """Start Minecraft"""
        self.play_button.configure(state="disabled")

        # Install win
        install_window = InstallWindow()
        self.wait_window(install_window)

        env = install_window.environment
        if env is None:
            self.play_button.configure(state="normal")
            return

        # Run win
        run_window = RunWindow(environment=env)
        self.wait_window(run_window)

        self.play_button.configure(state="normal")


class ScrollableFrame(customtkinter.CTkScrollableFrame):
    """A frame that contains the bulletin."""
    def __init__(self, master, mcmanager: MCManager=None):
        super().__init__(master)
        logger.debug("Creating scrollable frame")

        if mcmanager is None:
            raise ValueError("MCManager object is required")

        # Parse the bulletin config and create the bulletin
        bulletin_config: dict = mcmanager.remote_config.get("bulletin", None)
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
                    section_frame, text=section, font=SETTINGS.get_gui("font_title")
                )
                section_label.grid(row=section_row, column=0, padx=10, pady=10, sticky="n")
                section_row += 1
                item_row = section_row
                for i, item in enumerate(items):
                    pady = (10, 0) if i < len(items) - 1 else 10  # Add padding to the last item
                    item_label = utils.WrappingLabel(
                        section_frame, text=item, font=SETTINGS.get_gui("font_normal")
                    )
                    item_label.grid(row=item_row, column=0, padx=10, pady=pady, sticky="we")
                    item_row += 1

        logger.debug("Scrollable frame created")


class CenterFrame(customtkinter.CTkFrame):
    """This frame contains the bulletin."""
    def __init__(self, master, mcmanager: MCManager=None):
        super().__init__(master)
        logger.debug("Creating center frame")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=2)

        # Title Label
        self.title_label = customtkinter.CTkLabel(
            self, text="Server Bulletin", font=SETTINGS.get_gui("font_title")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="n")

        # Scrollable Frame
        self.scrollable_frame = ScrollableFrame(self, mcmanager=mcmanager)
        self.scrollable_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

        logger.debug("Center frame created")


class App(customtkinter.CTk):
    """The main window of the application."""
    def __init__(self):
        super().__init__()
        # pylint: disable=W0012
        # pylint: disable=E0606
        if SPLASH_FOUND:
            pyi_splash.update_text("Loading Prerequisites")
            logger.debug("Updated splash text")
            sleep(1)
        else:
            logger.warning("Splash screen not found")

        logger.debug("Creating main window")

        self.mc = MCManager(context=path.CONTEXT)

        self.title(path.PROGRAM_NAME)
        geom_length, geom_height = SETTINGS.get_gui("main_window_geometry")
        min_length, min_height = SETTINGS.get_gui("main_window_min_size")
        self.geometry(f"{geom_length}x{geom_height}")
        self.minsize(min_length, min_height)
        self.grid_rowconfigure(0, weight=1)  # configure grid system
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)

        customtkinter.set_appearance_mode(SETTINGS.get_gui("appearance"))

        if SPLASH_FOUND:
            pyi_splash.update_text("Loading Left Frame")
            logger.debug("Updated splash text")
            sleep(.25)
        self.settings_frame = LeftFrame(self)
        self.settings_frame.grid(row=0, column=0, padx=(10, 0), pady=10, sticky="nsw")

        if SPLASH_FOUND:
            pyi_splash.update_text("Loading Right Frame")
            logger.debug("Updated splash text")
            sleep(.25)
        self.right_frame = RightFrame(self, mcmanager=self.mc)
        self.right_frame.grid(row=0, column=2, padx=(0, 10), pady=10, sticky="nse")

        if SPLASH_FOUND:
            pyi_splash.update_text("Loading Center Frame")
            logger.debug("Updated splash text")
            sleep(.25)
        self.center_frame = CenterFrame(self, mcmanager=self.mc)
        self.center_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        logger.debug("Main window created")

        if SPLASH_FOUND:
            pyi_splash.close()
            logger.debug("Closed splash screen")
        # pylint: enable=E0606
        # pylint: enable=W0012
