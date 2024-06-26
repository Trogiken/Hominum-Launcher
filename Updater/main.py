"""
This module provides the main entry point for the application.
"""

import sys
import os
from source.gui.app_win import App

IS_DEVELOPMENT = True  # This should be set to False before release


if __name__ == "__main__":
    if not IS_DEVELOPMENT:
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        with open(os.devnull, 'w', encoding='utf-8') as devnull:
            sys.stdout = devnull
            sys.stderr = devnull

    try:
        app = App()
        app.mainloop()
    finally:
        sys.stdout.close()
        sys.stderr.close()
        if not IS_DEVELOPMENT:
            sys.stdout = original_stdout
            sys.stderr = original_stderr
