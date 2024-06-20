import threading
import customtkinter
from source.gui import utils
from source.pmc import MCManager
from source import path
from source import exceptions

SETTINGS = utils.get_settings()


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
