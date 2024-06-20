import customtkinter
from source.path import PROGRAM_NAME
from source.gui.login_win import LoginWindow
from source.gui import utils

SETTINGS = utils.get_settings()


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
