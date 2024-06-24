"""This module handles PortableMC"""

from portablemc.standard import Context, Environment, Watcher
from portablemc.fabric import FabricVersion


class MCManager:
    """MCManager is a class that handles PortableMC."""
    def __init__(self, context: Context):
        self.context = context

    def provision_version(self, version: str) -> FabricVersion:
        """
        Provisions a version for PortableMC.

        Returns:
        - FabricVersion: The version for PortableMC.
        """
        return FabricVersion.with_fabric(version, context=self.context)

    def provision_environment(self, version: FabricVersion, watcher: Watcher=None) -> Environment:
        """
        Provisions an environment for PortableMC.

        Returns:
        - Environment: The environment for PortableMC.
        """
        return version.install(watcher=watcher)
