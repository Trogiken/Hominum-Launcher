"""This module handles PortableMC"""

from pathlib import Path
from portablemc.standard import Context, Environment
from portablemc.fabric import FabricVersion


class MCManager:
    """MCManager is a class that handles PortableMC."""
    environment: Environment = None

    def __init__(self, context: Context):
        self.context = context

    def provision_version(self, version: str) -> FabricVersion:
        """
        Provisions a version for PortableMC.

        Returns:
        - FabricVersion: The version for PortableMC.
        """
        return FabricVersion.with_fabric(version, context=self.context)
