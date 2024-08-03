"""
Contains the SettingsWindow class.

Classes:
- ResetSettingsFrame: A frame for resetting the settings.
- JVMArgsWindow: A window for the JVM Arguments.
- GameSettingsFrame: A frame for the game settings.
- SettingsWindow: A window to display the settings of the launcher.
"""

import logging
import customtkinter
from source import path, utils
from source.gui.popup_win import PopupWindow
from source.mc.authentication import AuthenticationHandler

logger = logging.getLogger(__name__)


class ResetSettingsFrame(customtkinter.CTkFrame):
    """Frame for the reset settings."""
    def __init__(self, master):
        super().__init__(master)
        logger.debug("Creating GUI settings frame")

        self.settings = utils.Settings()

        self.popup_window = None
        self.grid_columnconfigure(0, weight=1)

        # Frame Title
        self.title_label = customtkinter.CTkLabel(
            self, text="Resets", font=self.settings.get_gui("font_title")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="n")

        # Reset GUI Settings Button
        self.reset_gui_settings_button = customtkinter.CTkButton(
            self,
            text="Reset GUI",
            font=self.settings.get_gui("font_normal"),
            command=self.reset_gui_settings
        )
        self.reset_gui_settings_button.grid(row=1, column=0, padx=20, pady=5, sticky="wse")

        # Reset User Settings Button
        self.reset_user_settings_button = customtkinter.CTkButton(
            self,
            text="Reset User",
            font=self.settings.get_gui("font_normal"),
            command=self.reset_user_settings
        )
        self.reset_user_settings_button.grid(row=2, column=0, padx=20, pady=5, sticky="wse")

        # Reset Game Settings Button
        self.reset_game_settings_button = customtkinter.CTkButton(
            self,
            text="Reset Game",
            font=self.settings.get_gui("font_normal"),
            command=self.reset_game_settings
        )
        self.reset_game_settings_button.grid(row=3, column=0, padx=20, pady=5, sticky="wse")

        # Reset All Settings Button
        self.reset_all_settings_button = customtkinter.CTkButton(
            self,
            text="Reset All",
            font=self.settings.get_gui("font_normal"),
            command=self.reset_all_settings
        )
        self.reset_all_settings_button.grid(row=4, column=0, padx=20, pady=(5, 20), sticky="wse")

        logger.debug("GUI settings frame created")

    def reset_gui_settings(self):
        """Reset the GUI settings to the default values."""
        if self.popup_window is not None and self.popup_window.winfo_exists():
            self.popup_window.lift()
        else:
            self.settings.reset_gui()
            self.popup_window = PopupWindow(
                master=self.master,
                title="GUI Reset",
                message="The GUI settings have been reset to default."
            )
            self.wait_window(self.popup_window)
            self.popup_window = None

    def reset_user_settings(self):
        """Reset the User settings to the default values."""
        if self.popup_window is not None and self.popup_window.winfo_exists():
            self.popup_window.lift()
        else:
            auth_handler = AuthenticationHandler(self.settings.get_user("email"), path.CONTEXT)
            auth_handler.remove_session()
            self.settings.reset_user()
            self.popup_window = PopupWindow(
                master=self.master,
                title="User Reset",
                message="The User settings have been reset to default."
            )
            self.wait_window(self.popup_window)
            self.popup_window = None

    def reset_game_settings(self):
        """Reset the Game settings to the default values."""
        if self.popup_window is not None and self.popup_window.winfo_exists():
            self.popup_window.lift()
        else:
            self.settings.reset_game()
            self.popup_window = PopupWindow(
                master=self.master,
                title="Game Reset",
                message="The Game settings have been reset to default."
            )
            self.wait_window(self.popup_window)
            self.popup_window = None

    def reset_all_settings(self):
        """Reset all settings to the default values."""
        if self.popup_window is not None and self.popup_window.winfo_exists():
            self.popup_window.lift()
        else:
            self.settings.reset()
            self.popup_window = PopupWindow(
                master=self.master,
                title="Settings Reset",
                message="All settings have been reset to default."
            )
            self.wait_window(self.popup_window)
            self.popup_window = None


class JVMArgsWindow(customtkinter.CTkToplevel):
    """Window for the JVM Arguments."""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        logger.debug("Creating JVM Arguments window")

        self.settings = utils.Settings()

        self.title("JVM Arguments")
        self.geometry("600x300")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(4, weight=1)

        self.attributes("-topmost", True)

        initial_heap, max_heap = self.settings.get_game("ram_jvm_args")
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
            self, text="Memory Allocation", font=self.settings.get_gui("font_large")
        )
        self.ram_slider_label.grid(row=0, column=0, padx=20, pady=(20, 0))

        # Ram Slider Value Label
        self.ram_value_var = customtkinter.IntVar(value=self.current_ram_allocation)
        self.ram_slider_value_label = customtkinter.CTkLabel(
            self,
            text=f"RAM: {self.ram_value_var.get()} MB",
            font=self.settings.get_gui("font_normal")
        )
        self.ram_slider_value_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")

        # Ram Slider
        self.ram_slider = customtkinter.CTkSlider(
            self,
            from_=1024,
            to=16384,
            number_of_steps=30,
            variable=self.ram_value_var,
            command=self.slider_event
        )
        self.ram_slider.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="we")

        # JVM Arguments Label
        self.jvm_args_label = customtkinter.CTkLabel(
            self, text="Additional JVM Arguments", font=self.settings.get_gui("font_large")
        )
        self.jvm_args_label.grid(row=3, column=0, padx=20, pady=(0, 10))

        # JVM Arguments Entry
        self.jvm_args_entry = customtkinter.CTkEntry(
            self, font=self.settings.get_gui("font_normal"), width=300
        )
        self.jvm_args_entry.insert(0, " ".join(self.settings.get_game("additional_jvm_args")))
        self.jvm_args_entry.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="we")

        # Save Button
        self.save_button = customtkinter.CTkButton(
            self,
            text="Save",
            width=160,
            height=32,
            font=self.settings.get_gui("font_large"),
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
        self.settings.set_game(ram_jvm_args=ram_jvm_args, additional_jvm_args=additional_jvm_args)
        self.destroy()


class GameSettingsFrame(customtkinter.CTkFrame):
    """Frame for the Game settings."""
    def __init__(self, master):
        super().__init__(master)
        logger.debug("Creating game settings frame")

        self.settings = utils.Settings()

        self.grid_columnconfigure(0, weight=1)

        self.jvm_args_window = None

        # Frame Title
        self.title_label = customtkinter.CTkLabel(
            self, text="Game", font=self.settings.get_gui("font_title")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="n")

        # Open MC Data Folder
        self.open_data_folder_button = customtkinter.CTkButton(
            self,
            text="Open Game Folder",
            font=self.settings.get_gui("font_normal"),
            command=self.open_data_folder,
        )
        self.open_data_folder_button.grid(row=1, column=0, padx=20, pady=5, sticky="wse")

        # JVM Arguments Entry
        self.jvm_args_button = customtkinter.CTkButton(
            self,
            text="Memory & Arguments",
            font=self.settings.get_gui("font_normal"),
            command=self.open_jvm_args_window
        )
        self.jvm_args_button.grid(row=2, column=0, padx=20, pady=(5, 20), sticky="wse")

        logger.debug("Game settings frame created")

    def open_data_folder(self):
        """Open the data folder"""
        utils.open_path(path.WORK_DIR)

    def open_jvm_args_window(self):
        """Open the JVM Arguments dialog."""
        if self.jvm_args_window is not None and self.jvm_args_window.winfo_exists():
            self.jvm_args_window.lift()
        else:
            self.jvm_args_window = JVMArgsWindow(self.master)
            self.jvm_args_window.transient(self)
            self.wait_window(self.jvm_args_window)
            self.jvm_args_window = None


class SettingsWindow(customtkinter.CTkToplevel):
    """A window to display the settings of the launcher."""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        logger.debug("Creating settings window")

        self.settings = utils.Settings()

        self.title("Settings")
        self.geometry("500x350")
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # GUI Settings Frame
        self.gui_settings_frame = ResetSettingsFrame(self)
        self.gui_settings_frame.grid(row=0, column=0, padx=20, pady=20, sticky="we")

        # Game Settings Frame
        self.game_settings_frame = GameSettingsFrame(self)
        self.game_settings_frame.grid(row=0, column=1, padx=20, pady=20, sticky="we")

        # Open Launcher Settings File
        self.open_settings_file_button = customtkinter.CTkButton(
            self,
            text="Open Launcher Settings",
            font=self.settings.get_gui("font_normal"),
            command=lambda: utils.open_path(self.settings.path)
        )
        self.open_settings_file_button.grid(
            row=1, column=0, columnspan=2, padx=20, pady=0, sticky="wne"
        )

        logger.debug("Settings window created")
