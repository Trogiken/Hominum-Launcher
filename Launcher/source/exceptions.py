"""
This module contains custom exceptions related to error handling.

Classes:
- DownloadError: Raised when a download fails.
- Base64DecodeError: Raised when a file fails to be decoded from base64.
- VersionInstallTimeout: Raised when a version failed to install.
- RemoteError: Raised when an error occurs with the remote server.
- GlobalKill: Raised when a global kill is requested.
"""

import logging

logger = logging.getLogger(__name__)


class DownloadError(Exception):
    """Raised when a download fails."""


class Base64DecodeError(Exception):
    """Raised when a file fails to be decoded from base64"""


class VersionInstallTimeout(Exception):
    """Raised when a version failed to install"""


class RemoteError(Exception):
    """Raised when an error occurs with the remote server."""


class GlobalKill(Exception):
    """Raised when a global kill is requested."""
    def __init__(self, message: str = "Global kill requested"):
        logger.debug(message)
        super().__init__()
