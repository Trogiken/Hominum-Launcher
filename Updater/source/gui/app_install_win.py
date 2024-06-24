import threading
import customtkinter
from portablemc.fabric import FabricVersion
from portablemc.standard import Watcher, DownloadCompleteEvent, DownloadProgressEvent, DownloadStartEvent
from source.utils import Settings
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
            self.app.update_label("Download Complete")


class VersionInstallWindow(customtkinter.CTkToplevel):
    def __init__(self, master, version: FabricVersion, **kwargs):
        super().__init__(master, **kwargs)
        self.title("Fabric Installation")
        self.version = version
        self.geometry("500x150")
        self.resizable(False, False)
        self.columnconfigure(0, weight=1)  # configure grid system
        self.rowconfigure(0, weight=1)

        # Make the window modal
        self.transient(master)  # Set to be a transient window of the master window
        self.grab_set()  # Direct all events to this window

        self.protocol("WM_DELETE_WINDOW", self.destroy)  # Handle the close event

        # Item Download Label
        self.download_item_label = customtkinter.CTkLabel(
            self, text="Download Starting", font=SETTINGS.get_gui("font_normal")
        )
        self.download_item_label.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        # Progress bar
        self.progress_bar = customtkinter.CTkProgressBar(self, mode="indeterminate")
        self.progress_bar.grid(row=1, column=0, columnspan=2, padx=20, pady=20, sticky="ew")
        self.progress_bar.start()

        self.install_thread = threading.Thread(target=self.install)
        self.install_thread.start()

        while self.install_thread.is_alive():
            self.update_idletasks()
            self.update()

        self.destroy()

    def install(self):
        install_watcher = InstallWatcher(self)
        MCManager.environment = self.version.install(watcher=install_watcher)

    def update_item(self, text):
        self.download_item_label.configure(text=text)

    def reset_progress(self):
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(0)

    def update_progress(self, value):
        self.progress_bar.set(value)
