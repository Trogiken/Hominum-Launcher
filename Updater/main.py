"""
This module provides the main entry point for the application.
"""

import sys
import os
from source.gui.app_win import App

# TODO: Remove print messages


if __name__ == "__main__":
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    sys.stdout = open(os.devnull, 'w', encoding='utf-8')
    sys.stderr = open(os.devnull, 'w', encoding='utf-8')

    try:
        app = App()
        app.mainloop()
    finally:
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = original_stdout
        sys.stderr = original_stderr
