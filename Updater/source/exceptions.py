"""
This module contains custom exceptions related to error handling.
"""

class DownloadError(Exception):
    """Raised when a download fails."""


class VersionInstallTimeout(Exception):
    """Raised when a version failed to install"""
