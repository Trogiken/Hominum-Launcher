import threading
import customtkinter
from portablemc.standard import \
Watcher, DownloadCompleteEvent, DownloadProgressEvent, DownloadStartEvent
from portablemc.fabric import FabricVersion
from source import path
from source.utils import Settings
from source.pmc.authentication import AuthenticationHandler
from source.pmc import MCManager

SETTINGS = Settings()


class InstallWatcher(Watcher):
    def __init__(self, master):
        self.app = master
        self.total = 0

    def handle(self, event) -> None:
        if isinstance(event, DownloadStartEvent):
            self.app.reset_progress()
            self.total = event.entries_count
        elif isinstance(event, DownloadProgressEvent):
            self.app.update_item(str(event.entry))
            self.app.update_progress(event.count / self.total)
        elif isinstance(event, DownloadCompleteEvent):
            self.app.update_item("Download Complete")


class InstallFrame(customtkinter.CTkFrame):
    def __init__(self, master, pmc: MCManager, version: FabricVersion, on_install_complete=None):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)

        self.pmc = pmc
        self.version = version
        self.on_install_complete = on_install_complete

        # Item Download Label
        self.download_item_label = customtkinter.CTkLabel(
            self, text="Download Starting", font=SETTINGS.get_gui("font_normal")
        )
        self.download_item_label.grid(row=0, column=0, padx=20, pady=20)

        # Progress bar
        self.progress_bar = customtkinter.CTkProgressBar(self, mode="indeterminate")
        self.progress_bar.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")
        self.progress_bar.start()

        self.start_installation()

    def start_installation(self):
        self.install_thread = threading.Thread(target=self.install)
        self.install_thread.start()
        self.check_thread()
    
    def check_thread(self):
        if self.install_thread.is_alive():
            # Check again after 100ms
            self.after(100, self.check_thread)
        else:
            # Thread is not alive, call the callback
            if self.on_install_complete:
                self.on_install_complete()

    def install(self):
        install_watcher = InstallWatcher(self)
        # Attempt to install 3 times
        for _ in range(3):
            try:
                self.version.install(watcher=install_watcher)
                self.on_install_complete()
                break
            except Exception as e:
                print(f"Error: {e}")

    def update_item(self, text):
        self.download_item_label.configure(text=text)

    def reset_progress(self):
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(0)

    def update_progress(self, value):
        self.progress_bar.set(value)


class RunFrame(customtkinter.CTkFrame):
    def __init__(self, master, pmc: MCManager, version: FabricVersion, on_run_complete=None):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)

        self.pmc = pmc
        self.version = version
        self.on_run_complete = on_run_complete

        self.title_label = customtkinter.CTkLabel(
            self, text="Game Running", font=SETTINGS.get_gui("font_large")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=20)

        self.message_label = customtkinter.CTkLabel(
            self,
            text="Please wait until the Minecraft window opens",
            font=SETTINGS.get_gui("font_normal")
        )
        self.message_label.grid(row=1, column=0, padx=20, pady=(0, 20))

        self.run_game()

    def run_game(self):
        self.game_thread = threading.Thread(target=self.run)
        self.game_thread.start()
        self.check_thread()

    def check_thread(self):
        if self.game_thread.is_alive():
            # Check again after 100ms
            self.after(100, self.check_thread)
        else:
            # Thread is not alive, call the callback
            if self.on_run_complete:
                self.on_run_complete()
    
    def run(self):
        env = self.pmc.provision_environment(self.version)
        env.run()


class RunGameWindow(customtkinter.CTkToplevel):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.title("Run Game")
        self.pmc = MCManager(context=path.CONTEXT)
        self.auth_handler = AuthenticationHandler(email=SETTINGS.get_user("email"), context=path.CONTEXT)
        self.version = self.pmc.provision_version("1.20.6")
        session = self.auth_handler.refresh_session()
        if session is None:
            print("No Auth")
            return
        self.version.auth_session = session

        self.geometry("500x150")
        self.resizable(False, False)
        self.columnconfigure(0, weight=1)  # configure grid system
        self.rowconfigure(0, weight=1)

        # Make the window modal
        self.transient(master)  # Set to be a transient window of the master window
        self.grab_set()  # Direct all events to this window

        self.protocol("WM_DELETE_WINDOW", self.destroy)  # Handle the close event

        # create install frame
        self.install_frame = InstallFrame(
            self, self.pmc, self.version, on_install_complete=self.on_install_complete
        )
        self.install_frame.grid(row=0, column=0, sticky="nsew")

    def on_install_complete(self):
        self.install_frame.destroy()
        run_frame = RunFrame(self, self.pmc, self.version, on_run_complete=self.on_run_complete)
        run_frame.grid(row=0, column=0, sticky="nsew")

    def on_run_complete(self):
        self.destroy()
