"""
This module contains custom exceptions related to error handling.
"""

import logging

logger = logging.getLogger(__name__)


class DownloadError(Exception):
    """Raised when a download fails."""


class VersionInstallTimeout(Exception):
    """Raised when a version failed to install"""


class RemoteError(Exception):
    """Raised when an error occurs with the remote server."""


class GlobalKill(Exception):
    """Raised when a global kill is requested."""
    def __init__(self, message: str = "Global kill requested"):
        logger.debug(message)
        super().__init__()
