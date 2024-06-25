"""This module handles PortableMC"""

from portablemc.standard import Context, Environment, Watcher
from portablemc.fabric import FabricVersion
from source.mc import remote


class MCManager:
    """MCManager is a class that handles Minecraft"""
    def __init__(self, context: Context):
        self.context = context
        self.remote_config = remote.get_config()

    def provision_version(self, vanilla_version: str, loader_version: str=None) -> FabricVersion:
        """
        Provisions a version for PortableMC.

        Parameters:
        - vanilla_version (str): The fabric version.
        - loader_version (str): The loader version. Defaults to latest.

        Returns:
        - FabricVersion: The version for PortableMC.
        """
        return FabricVersion.with_fabric(
            vanilla_version=vanilla_version, loader_version=loader_version, context=self.context
        )

    def provision_environment(self, version: FabricVersion, watcher: Watcher=None) -> Environment:
        """
        Provisions an environment for PortableMC.

        Returns:
        - Environment: The environment for PortableMC.
        """
        return version.install(watcher=watcher)

    @property
    def server_ip(self) -> str:
        """The server IP."""
        return self.remote_config["client"]["server_ip"]

    @property
    def fabric_version(self) -> str:
        """The fabric version."""
        return self.remote_config["client"]["fabric_version"]

    @property
    def loader_version(self) -> str | None:
        """The loader version."""
        return self.remote_config["client"]["loader_version"]
