"""
This module contains the SettingsWindow class,
which represents the settings window of the application.

Classes:
- GUISettingsFrame: A frame for the GUI settings.
- UserSettingsFrame: A frame for the User settings.
- GameSettingsFrame: A frame for the Game settings.
- SettingsWindow: A window for the settings of the application.
"""

import logging
import customtkinter
from source import path
from source.utils import Settings, open_directory
from source.gui.popup_win import PopupWindow
from source.mc.authentication import AuthenticationHandler

logger = logging.getLogger(__name__)

SETTINGS = Settings()


class GUISettingsFrame(customtkinter.CTkFrame):
    """A frame for the GUI settings."""
    def __init__(self, master):
        super().__init__(master)
        logger.debug("Creating GUI settings frame")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Frame Title
        self.title_label = customtkinter.CTkLabel(
            self, text="GUI", font=SETTINGS.get_gui("font_title")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="n")

        # Reset GUI Settings Button
        self.reset_gui_settings_button = customtkinter.CTkButton(
            self,
            text="Reset Settings",
            font=SETTINGS.get_gui("font_normal"),
            command=self.reset_gui_settings
        )
        self.reset_gui_settings_button.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="s")

        logger.debug("GUI settings frame created")

    def reset_gui_settings(self):
        """Reset the GUI settings to the default values."""
        SETTINGS.reset_gui()
        PopupWindow(
            master=self.master,
            title="Settings Reset",
            message="The GUI settings have been reset to default."
        )


class UserSettingsFrame(customtkinter.CTkFrame):
    """A frame for the User settings."""
    def __init__(self, master):
        super().__init__(master)
        logger.debug("Creating user settings frame")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Frame Title
        self.title_label = customtkinter.CTkLabel(
            self, text="User", font=SETTINGS.get_gui("font_title")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="n")

        # Reset User Settings Button
        self.reset_user_settings_button = customtkinter.CTkButton(
            self,
            text="Reset Settings",
            font=SETTINGS.get_gui("font_normal"),
            command=self.reset_user_settings
        )
        self.reset_user_settings_button.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="s")

        logger.debug("User settings frame created")

    def reset_user_settings(self):
        """Reset the User settings to the default values."""
        auth_handler = AuthenticationHandler(SETTINGS.get_user("email"), path.CONTEXT)
        auth_handler.remove_session()
        SETTINGS.reset_user()
        PopupWindow(
            master=self.master,
            title="Settings Reset",
            message="The User settings have been reset to default."
        )


class JVMArgsWindow(customtkinter.CTkToplevel):
    """A window for the JVM Arguments."""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        logger.debug("Creating JVM Arguments window")

        self.title("JVM Arguments")
        self.geometry("600x300")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(4, weight=1)

        self.attributes("-topmost", True)

        initial_heap, max_heap = SETTINGS.get_game("ram_jvm_args")
        # Get the number from the JVM Arguments
        initial_heap = int(initial_heap.split("-Xms")[1].replace("M", ""))
        max_heap = int(max_heap.split("-Xmx")[1].replace("M", ""))
        if initial_heap == max_heap:
            self.current_ram_allocation = initial_heap
        else:
            logger.warning("Initial and Max heap sizes are not equal. Using Max heap size.")
            self.current_ram_allocation = max_heap

        # Ram Slider Label
        self.ram_slider_label = customtkinter.CTkLabel(
            self, text="Memory Allocation", font=SETTINGS.get_gui("font_large")
        )
        self.ram_slider_label.grid(row=0, column=0, padx=20, pady=(20, 0))
        # Ram Slider Value Label
        self.ram_value_var = customtkinter.IntVar(value=self.current_ram_allocation)
        self.ram_slider_value_label = customtkinter.CTkLabel(
            self, text=f"RAM: {self.ram_value_var.get()} MB", font=SETTINGS.get_gui("font_normal")
        )
        self.ram_slider_value_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        # Ram Slider
        self.ram_slider = customtkinter.CTkSlider(
            self,
            from_=512,
            to=16384,
            number_of_steps=512,
            variable=self.ram_value_var,
            command=self.slider_event
        )
        self.ram_slider.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="we")

        # JVM Arguments Label
        self.jvm_args_label = customtkinter.CTkLabel(
            self, text="Additional JVM Arguments", font=SETTINGS.get_gui("font_large")
        )
        self.jvm_args_label.grid(row=3, column=0, padx=20, pady=(0, 10))
        # JVM Arguments Entry
        self.jvm_args_entry = customtkinter.CTkEntry(
            self, font=SETTINGS.get_gui("font_normal"), width=300
        )
        self.jvm_args_entry.insert(0, " ".join(SETTINGS.get_game("additional_jvm_args")))
        self.jvm_args_entry.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="we")

        # Save Button
        self.save_button = customtkinter.CTkButton(
            self,
            text="Save",
            width=160,
            height=32,
            font=SETTINGS.get_gui("font_large"),
            command=self.save_jvm_args
        )
        self.save_button.grid(row=5, column=0, padx=20, pady=(0, 20), sticky="s")

        logger.debug("JVM Arguments window created")

    def slider_event(self, value):
        """Update the value label when the slider is moved."""
        self.ram_value_var.set(int(value))
        self.ram_slider_value_label.configure(text=f"RAM: {self.ram_value_var.get()} MB")

    def save_jvm_args(self):
        """Save the JVM Arguments to the settings."""
        ram_jvm_args = [f"-Xms{self.ram_value_var.get()}M", f"-Xmx{self.ram_value_var.get()}M"]
        additional_jvm_args = self.jvm_args_entry.get().split()
        additional_jvm_args = list(filter(None, additional_jvm_args))  # filter out empty strings
        SETTINGS.set_game(ram_jvm_args=ram_jvm_args, additional_jvm_args=additional_jvm_args)
        self.destroy()


class GameSettingsFrame(customtkinter.CTkFrame):
    """A frame for the Game settings."""
    def __init__(self, master):
        super().__init__(master)
        logger.debug("Creating game settings frame")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.jvm_args_window = None

        # Frame Title
        self.title_label = customtkinter.CTkLabel(
            self, text="Game", font=SETTINGS.get_gui("font_title")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="n")

        # Open MC Data Folder
        self.open_data_folder_button = customtkinter.CTkButton(
            self,
            text="Open Game Folder",
            font=SETTINGS.get_gui("font_normal"),
            command=self.open_data_folder,
        )
        self.open_data_folder_button.grid(row=1, column=0, padx=20, pady=5)

        # JVM Arguments Entry
        self.jvm_args_button = customtkinter.CTkButton(
            self,
            text="JVM Arguments",
            font=SETTINGS.get_gui("font_normal"),
            command=self.open_jvm_args_window
        )
        self.jvm_args_button.grid(row=2, column=0, padx=20, pady=5)

        # Reset Game Settings Button
        self.reset_game_settings_button = customtkinter.CTkButton(
            self,
            text="Reset Settings",
            font=SETTINGS.get_gui("font_normal"),
            command=self.reset_game_settings
        )
        self.reset_game_settings_button.grid(row=3, column=0, padx=20, pady=(5, 20), sticky="s")

        logger.debug("Game settings frame created")

    def open_data_folder(self):
        """Open the data folder"""
        open_directory(path.WORK_DIR)

    def open_jvm_args_window(self):
        """Open the JVM Arguments dialog."""
        if self.jvm_args_window is not None and self.jvm_args_window.winfo_exists():
            self.jvm_args_window.lift()
        else:
            self.jvm_args_window = JVMArgsWindow(self.master)
            self.jvm_args_window.transient(self)
            self.wait_window(self.jvm_args_window)
            self.jvm_args_window = None

    def reset_game_settings(self):
        """Reset the Game settings to the default values."""
        SETTINGS.reset_game()
        PopupWindow(
            master=self.master,
            title="Settings Reset",
            message="The Game settings have been reset to default."
        )


class SettingsWindow(customtkinter.CTkToplevel):
    """A window for the settings of the application."""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        logger.debug("Creating settings window")

        self.title("Settings")
        self.geometry("600x300")
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # GUI Settings Frame
        self.gui_settings_frame = GUISettingsFrame(self)
        self.gui_settings_frame.grid(row=0, column=0, padx=(20, 0), pady=20)

        # User Settings Frame
        self.user_settings_frame = UserSettingsFrame(self)
        self.user_settings_frame.grid(row=0, column=1, padx=20, pady=20)

        # Game Settings Frame
        self.game_settings_frame = GameSettingsFrame(self)
        self.game_settings_frame.grid(row=0, column=2, padx=(0, 20), pady=20)

        # Reset all button
        self.reset_all_button = customtkinter.CTkButton(
            self,
            text="Reset All Settings",
            font=SETTINGS.get_gui("font_large"),
            command=self.reset_all_settings
        )
        self.reset_all_button.grid(
            row=1, column=0, columnspan=3, padx=20, pady=(0, 20), sticky="wes"
        )

        logger.debug("Settings window created")

    def reset_all_settings(self):
        """Reset all settings to the default values."""
        SETTINGS.reset()
        PopupWindow(
            master=self.master,
            title="Settings Reset",
            message="All settings have been reset to default."
        )
        self.destroy()
