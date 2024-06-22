"""
This module contains the SettingsWindow class.

Classes:
- SettingsWindow: Represents the setting window of the application.
"""

import customtkinter
from source import utils
from source.gui.popup_win import PopupWindow

SETTINGS = utils.get_settings()


class GUISettingsFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Frame Title
        self.title_label = customtkinter.CTkLabel(
            self, text="GUI Settings", font=SETTINGS.gui.font_large
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=20, sticky="n")

        # Reset GUI Settings Button
        self.reset_gui_settings_button = customtkinter.CTkButton(
            self,
            text="Reset GUI",
            font=SETTINGS.gui.font_normal,
            command=self.reset_gui_settings
        )
        self.reset_gui_settings_button.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="s")

    def reset_gui_settings(self):
        """Reset the GUI settings to the default values."""
        utils.reset_settings()
        PopupWindow(
            master=self.master,
            title="Settings Reset",
            message="The GUI settings have been reset to default."
        )


class SettingsWindow(customtkinter.CTkToplevel):
    """
    Represents the setting window of the application.

    Methods:
        __init__: Initializes the SettingsWindow instance.
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.title("Settings")
        self.geometry("450x200")
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # GUI Settings Frame
        self.gui_settings_frame = GUISettingsFrame(self)
        self.gui_settings_frame.grid(row=0, column=0, padx=20, pady=20, sticky="n")
