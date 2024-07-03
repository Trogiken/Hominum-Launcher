"""
This module provides the main entry point for the application.

Logging is configured and the main application loop is started.
"""

import logging
import logging.config
import logging.handlers
from datetime import datetime
import sys
import os
from source.gui.app_win import App
from source import path

# FIXME: Doesn't work right when compiled

IS_DEVELOPMENT = True  # This should be set to False before release


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
    root_logger.setLevel(logging.DEBUG if IS_DEVELOPMENT else logging.INFO)
    root_logger.addHandler(error_tracker)  # Attach the error handler to the root logger
    root_logger.addHandler(file_handler)
    if IS_DEVELOPMENT:
        root_logger.addHandler(console_handler)

    return error_tracker


if __name__ == "__main__":
    application_errors = configure_logging()
    logger = logging.getLogger(__name__)

    # log constants
    logger.info("PROGRAM_NAME: %s", path.PROGRAM_NAME)
    logger.info("PROGRAM_NAME_LONG: %s", path.PROGRAM_NAME_LONG)
    logger.info("VERSION: %s", path.VERSION)
    logger.info("APPLICATION_DIR: %s", path.APPLICATION_DIR)
    logger.info("ASSETS_DIR: %s", path.ASSETS_DIR)
    logger.info("STORE_DIR: %s", path.STORE_DIR)
    logger.info("MAIN_DIR: %s", path.MAIN_DIR)
    logger.info("WORK_DIR: %s", path.WORK_DIR)

    if not IS_DEVELOPMENT:
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        with open(os.devnull, 'w', encoding='utf-8') as devnull:
            sys.stdout = devnull
            sys.stderr = devnull

    try:
        logger.info("Starting application")
        app = App()
        app.mainloop()
        if application_errors.error_occurred:
            logger.warning("Application finished with errors")
            for error in application_errors.errors:
                logger.warning(error)
        else:
            logger.info("Application finished successfully")
    except Exception as e:
        logger.exception("An unhandled exception occurred")
        raise
    finally:
        if not IS_DEVELOPMENT:
            sys.stdout.close()
            sys.stderr.close()
            sys.stdout = original_stdout
            sys.stderr = original_stderr
