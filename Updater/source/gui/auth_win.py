"""
This module contains the AuthWindow class.

Classes:
- AuthWindow: Toplevel window for authenticating the user with the Minecraft account.
"""

import threading
import customtkinter
from source.gui import utils
from source.pmc import MCManager
from source import path
from source import exceptions

SETTINGS = utils.get_settings().GUISettings


class AuthWindow(customtkinter.CTkToplevel):
    """
    Toplevel window for authenticating the user with a Minecraft account.

    Methods:
    - __init__: Initializes the AuthWindow instance.
    - auth: Runs the authentication process.
    """
    def __init__(self, master, email, **kwargs):
        super().__init__(master, **kwargs)
        self.title("Authentication")
        self.email = email
        self.geometry("400x100")
        self.resizable(False, False)
        self.columnconfigure(0, weight=1)  # configure grid system

        # Make the window modal
        self.transient(master)  # Set to be a transient window of the master window
        self.grab_set()  # Direct all events to this window

        self.protocol("WM_DELETE_WINDOW", self.destroy)  # Handle the close event

        self.label = customtkinter.CTkLabel(
            self, text=f"Logging into {self.email}", font=SETTINGS.font_large
        )
        self.label.grid(row=0, column=0, pady=(20, 0))

        self.progress = customtkinter.CTkProgressBar(self, mode="indeterminate")
        self.progress.grid(row=1, column=0, pady=(20, 0))
        self.progress.start()

        auth_thread = threading.Thread(target=self.auth, daemon=True)
        auth_thread.start()

        while auth_thread.is_alive():
            self.update_idletasks()
            self.update()

        self.destroy()

    def auth(self):
        """Runs the authentication process. WORKING PROGRESS"""
        pmc = MCManager(context=(path.MAIN_DIR, path.WORK_DIR))
        try:
            pmc.authenticate(self.email)

            if MCManager.auth_session is None:
                raise exceptions.AuthenticationFailed("No auth session")
        except Exception:
            # TODO: Handle this
            print("Login failed")
