"""This module handles PortableMC"""

from portablemc.standard import Context, Version
from portablemc.fabric import FabricVersion
from portablemc.auth import MicrosoftAuthSession
from source.pmc.authentication import AuthenticationHandler


class MCManager:
    """MCManager is a class that handles PortableMC."""
    def __init__(self, email: str, context: tuple[str, str]):
        self.email = email
        self.context = Context(*context)
        self.auth_handler = AuthenticationHandler(self.email, self.context)

    def provision_version(self) -> Version:
        """
        Provisions a version for PortableMC.

        Parameters:
        - context (Context): The context for PortableMC.

        Returns:
        - Version: The version for PortableMC.
        """
        return FabricVersion.with_fabric("1.20.6", context=self.context)

    def authenticate(self) -> MicrosoftAuthSession:
        """
        Authenticates the user.

        Returns:
        - MicrosoftAuthSession: The Microsoft authentication session.
        """
        return self.auth_handler.microsoft_authenticate()
