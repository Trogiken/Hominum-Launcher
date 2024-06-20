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

import threading
import customtkinter
from source.pmc.main import MCManager
from source import path
from source import exceptions
from source import gui

PROGRAM_NAME = "Hominum"
VERSION = "4.5.3.4"
SETTINGS = gui.get_settings()


class AuthWindow(customtkinter.CTkToplevel):
    def __init__(self, master, email, **kwargs):
        super().__init__(master, **kwargs)
        self.title("Authentication")
        self.focus_set()
        self.email = email
        self.geometry("400x100")
        self.resizable(False, False)
        self.columnconfigure(0, weight=1)  # configure grid system

        self.label = customtkinter.CTkLabel(self, text=f"Logging into {self.email}", font=SETTINGS.font_large)
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
        pmc = MCManager(email=self.email, context=(path.MAIN_DIR, path.WORK_DIR))
        try:
            auth_session = pmc.authenticate()
            print(auth_session)

            if auth_session is None:
                raise exceptions.AuthenticationFailed("Auth session is None")
        except Exception:
            print("Login failed")


class LoginWindow(customtkinter.CTkToplevel):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.title("Login")
        self.geometry("450x200")
        self.resizable(False, False)
        self.grid_columnconfigure(0, weight=1)  # configure grid system

        # email label
        self.label = customtkinter.CTkLabel(self, text="Microsoft Email Address", font=SETTINGS.font_large)
        self.label.grid(row=0, column=0, pady=(20, 0))
        # email entry
        self.entry = customtkinter.CTkEntry(self, width=200)
        self.entry.grid(row=1, column=0, pady=(20, 0))
        self.entry.bind("<Return>", lambda _: self.login())
        # button
        self.button = customtkinter.CTkButton(self, text="Login", command=self.login, font=SETTINGS.font)
        self.button.grid(row=2, column=0, pady=(20, 0))

    def login(self):
        self.button.configure(state="disabled")
        # create top level window
        self.auth_window = AuthWindow(master=self.master, email=self.entry.get())
        self.destroy()

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title(PROGRAM_NAME)
        self.geometry("450x200")
        self.minsize(450, 200)
        self.grid_rowconfigure(0, weight=1)  # configure grid system
        self.grid_columnconfigure(0, weight=1)

        # TODO: if not logged in show login window and wait for login
        self.login_window = LoginWindow(master=self)
        self.login_window.transient(self)
        self.wait_window(self.login_window)

        # TODO: if logged in show main window, else show error message and repeat login
        self.focus_force()
        self.main_window = customtkinter.CTkLabel(self, text="Logged in", font=SETTINGS.font_large)
        self.main_window.grid(row=0, column=0)


if __name__ == "__main__":
    app = App()
    app.mainloop()
