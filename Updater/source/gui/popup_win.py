"""
This module contains the PopupWindow class, which represents a popup window.
"""

import customtkinter
from source.utils import Settings

SETTINGS = Settings()


class PopupWindow(customtkinter.CTkToplevel):
    """Popup window."""
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
            self, text=message, font=SETTINGS.get_gui("font_large")
        )
        self.label.grid(row=0, column=0, pady=(20, 0))

        self.button = customtkinter.CTkButton(
            self, text="OK", command=self.destroy, font=SETTINGS.get_gui("font_normal")
        )
        self.button.grid(row=1, column=0, pady=(20, 0))

        self.wait_window()
