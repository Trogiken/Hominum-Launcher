"""
Contains the PopupWindow class

Classes:
- PopupWindow: Popup window
- StandalonePopupWindow: Standalone popup window
"""

import logging
import customtkinter
from source import utils

logger = logging.getLogger(__name__)


class PopupWindow(customtkinter.CTkToplevel):
    """Popup window for displaying messages."""
    def __init__(self, master, title, message, **kwargs):
        super().__init__(master, **kwargs)
        logger.debug("Creating popup window")

        self.settings = utils.Settings()

        logger.debug("Popup window title: %s", title)
        logger.debug("Popup window message: %s", message)

        self.title(title)
        self.attributes("-topmost", True)
        self.transient(master)
        self.geometry("500x200")
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Scrollable frame
        self.message_frame = customtkinter.CTkScrollableFrame(self)
        self.message_frame.grid(row=0, column=0, padx=20, pady=20, sticky="new")

        self.label = customtkinter.CTkLabel(
            self.message_frame,
            text=message,
            font=self.settings.get_gui("font_large"), wraplength=400
        )
        self.label.grid(row=0, column=0, padx=20, pady=20)

        self.button = customtkinter.CTkButton(
            self, text="OK", command=self.destroy, font=self.settings.get_gui("font_normal")
        )
        self.button.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="s")

        logger.debug("Popup window created")


class StandalonePopupWindow(customtkinter.CTk):
    """Standalone popup window for displaying messages."""
    def __init__(self, title, message, **kwargs):
        super().__init__(**kwargs)
        logger.debug("Creating standalone popup window")

        self.settings = utils.Settings()

        logger.debug("Standalone Popup window title: %s", title)
        logger.debug("Standalone Popup window message: %s", message)

        self.title(title)
        self.geometry("500x200")
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Scrollable frame
        self.message_frame = customtkinter.CTkScrollableFrame(self)
        self.message_frame.grid(row=0, column=0, padx=20, pady=20, sticky="new")

        self.label = customtkinter.CTkLabel(
            self.message_frame,
            text=message,
            font=self.settings.get_gui("font_large"), wraplength=400
        )
        self.label.grid(row=0, column=0, padx=20, pady=20)

        self.button = customtkinter.CTkButton(
            self, text="OK", command=self.destroy, font=self.settings.get_gui("font_normal")
        )
        self.button.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="s")

        logger.debug("Standalone popup window created")
