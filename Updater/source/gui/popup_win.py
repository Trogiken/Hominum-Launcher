"""
This module contains the PopupWindow class, which represents a popup window.
"""

import logging
import customtkinter
from source.utils import Settings

logger = logging.getLogger(__name__)

SETTINGS = Settings()


class PopupWindow(customtkinter.CTkToplevel):
    """Popup window."""
    def __init__(self, master, title, message, **kwargs):
        super().__init__(master, **kwargs)
        logger.debug("Creating popup window")

        logger.debug("Popup window title: %s", title)
        logger.debug("Popup window message: %s", message)

        self.title(title)
        self.attributes("-topmost", True)
        self.geometry("500x200")
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Make the window modal
        self.transient(master)  # Set to be a transient window of the master window

        # Scrollable frame
        self.message_frame = customtkinter.CTkScrollableFrame(self)
        self.message_frame.grid(row=0, column=0, padx=20, pady=20, sticky="new")

        self.label = customtkinter.CTkLabel(
            self.message_frame, text=message, font=SETTINGS.get_gui("font_large"), wraplength=400
        )
        self.label.grid(row=0, column=0, padx=20, pady=20)

        self.button = customtkinter.CTkButton(
            self, text="OK", command=self.destroy, font=SETTINGS.get_gui("font_normal")
        )
        self.button.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="s")

        logger.debug("Popup window created")

        self.wait_window()  # Wait for the window to be destroyed
