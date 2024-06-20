"""
This module contains the main functionality for the Hominum Client program.
It provides a GUI interface for syncing mods with a server.

Functions:
- sync_mods(mods_path: str) -> None: Syncs mods with the server.
- main() -> None: Runs the main GUI program.

Constants:
- PROGRAM_NAME: The name of the program.
- VERSION: The version of the program.
"""

import customtkinter
from source.pmc.main import MCManager
from source import path
from source import exceptions
from source import gui

PROGRAM_NAME = "Hominum Client"
VERSION = "4.5.3.4"

MAIN_DIR = path.MAIN_DIR
WORK_DIR = path.USER_APP_PATH

SETTINGS = gui.get_settings()


class LoginFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid_columnconfigure(0, weight=1)  # configure grid system

        self.label = customtkinter.CTkLabel(self, text="Enter your microsoft email address", font=(SETTINGS.font_type, SETTINGS.font_size_large))
        self.label.grid(row=0, column=0, pady=(20, 0))
        # email entry
        self.entry = customtkinter.CTkEntry(self, width=200)
        self.entry.grid(row=1, column=0, pady=(20, 0))
        # button
        self.button = customtkinter.CTkButton(self, text="Login", command=self.login, font=SETTINGS.font)
        self.button.grid(row=2, column=0, pady=(20, 0))

    def login(self):
        self.label.configure(text="Logging in...")
        pmc = MCManager(email=self.entry.get(), context=(MAIN_DIR, WORK_DIR))
        try:
            auth_session = pmc.authenticate()

            if auth_session is None:
                raise exceptions.AuthenticationFailed()
        except Exception:
            self.label.configure(text="Login failed. Please try again.")


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("450x200")
        self.minsize(450, 200)
        self.grid_rowconfigure(0, weight=1)  # configure grid system
        self.grid_columnconfigure(0, weight=1)

        self.my_frame = LoginFrame(master=self)
        self.my_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")


if __name__ == "__main__":
    app = App()
    app.mainloop()
