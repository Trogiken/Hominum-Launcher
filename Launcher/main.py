"""
This module provides the main entry point for the application.

Logging is configured and the main application loop is started.
"""

import logging
import logging.config
import logging.handlers
import os
import sys
from datetime import datetime
import psutil
from source.gui.app_win import App
from source import path

IS_DEVELOPMENT = False  # This should be set to False before release


class ErrorTrackingHandler(logging.Handler):
    """A custom logging handler that tracks if an error occurred."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_occurred = False
        self.errors = []

    def emit(self, record):
        if record.levelno >= logging.ERROR:
            self.errors.append(record)
            self.error_occurred = True


def configure_logging():
    """
    Configures the logging for the application.

    Returns:
    - ErrorTrackingHandler: The error tracking handler used to track if an error occurred.
    """
    log_directory = path.APPLICATION_DIR / "logs"
    log_directory.mkdir(parents=True, exist_ok=True)

    # Naming the log file with a timestamp to ensure uniqueness
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = log_directory / f"hominum_{timestamp}.log"

    # Limit the amount of log files
    backup_count = 10
    log_files = os.listdir(log_directory)
    if len(log_files) >= backup_count:
        log_files.sort()  # Sort by creation time
        # Remove oldest logs until the limit is satisfied
        for _ in range((len(log_files) - backup_count) + 1):  # +1 to account for the latest log
            os.remove(os.path.join(log_directory, log_files.pop(0)))  # Remove the oldest log

    log_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(filename)-8s %(funcName)-10s %(lineno)04d | %(message)s",
        datefmt="%Y:%m:%d %H:%M:%S",
    )

    error_tracker = ErrorTrackingHandler()
    error_tracker.setFormatter(log_formatter)

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(log_formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)

    # setup logging for the application
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)  # Mute connectionpool
    logging.getLogger("httpx").setLevel(logging.WARNING)  # Mute httpx
    logging.getLogger("http").setLevel(logging.WARNING)  # Mute http
    root_logger.addHandler(error_tracker)  # Attach the error handler to the root logger
    root_logger.addHandler(file_handler)
    if IS_DEVELOPMENT:
        root_logger.addHandler(console_handler)

    return error_tracker


def is_process_running():
    """Check if there is any running process that contains the given name process_name."""
    process_names = ["hominum", "hominum.exe"]  # TODO: Make sure this is cross-platform
    appearance_count = 0
    for proc in psutil.process_iter(['name']):
        try:
            for process_name in process_names:
                if process_name.lower() in proc.info['name'].lower():
                    appearance_count += 1
                    if appearance_count > 1:
                        return True
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def exit_application(code: int=0):
    """Exit the application."""
    sys.exit(code)


if __name__ == "__main__":
    application_errors = configure_logging()
    logger = logging.getLogger(__name__)

    if not IS_DEVELOPMENT and is_process_running():
        logger.critical("Another instance of the updater is already running. Exiting...")
        exit_application(1)

    # log constants
    logger.info("PROGRAM_NAME: %s", path.PROGRAM_NAME)
    logger.info("PROGRAM_NAME_LONG: %s", path.PROGRAM_NAME_LONG)
    logger.info("VERSION: %s", path.VERSION)
    logger.info("APPLICATION_DIR: %s", path.APPLICATION_DIR)
    logger.info("ASSETS_DIR: %s", path.ASSETS_DIR)
    logger.info("STORE_DIR: %s", path.STORE_DIR)
    logger.info("MAIN_DIR: %s", path.MAIN_DIR)
    logger.info("WORK_DIR: %s", path.WORK_DIR)

    try:
        logger.info("Starting application")
        app = App()
        app.mainloop()
        if application_errors.error_occurred:
            logger.warning("Application finished with errors")
            for error in application_errors.errors:
                logger.warning(error)
            exit_application(1)
        else:
            logger.info("Application finished successfully")
            exit_application(0)
    except Exception as e:
        logger.exception("An unhandled exception occurred")
        exit_application(1)
