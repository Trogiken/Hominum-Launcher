"""This module contains the popup window class.

Classes:
- PopupWindow: Represents a popup window.
"""

import customtkinter
from source.gui import utils

SETTINGS = utils.get_settings().GUISettings


class PopupWindow(customtkinter.CTkToplevel):
    """
    Represents a popup window.

    Methods:
        __init__: Initializes the PopupWindow instance.
    """

    def __init__(self, master, title, message, **kwargs):
        super().__init__(master, **kwargs)
        self.title(title)
        self.geometry("400x100")
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)

        # Make the window modal
        self.transient(master)  # Set to be a transient window of the master window
        self.grab_set()  # Direct all events to this window

        self.protocol("WM_DELETE_WINDOW", self.destroy)  # Handle the close event

        self.label = customtkinter.CTkLabel(
            self, text=message, font=SETTINGS.font_large
        )
        self.label.grid(row=0, column=0, pady=(20, 0))

        self.button = customtkinter.CTkButton(
            self, text="OK", command=self.destroy, font=SETTINGS.font_normal
        )
        self.button.grid(row=1, column=0, pady=(20, 0))

        self.wait_window()
