"""This module handles PortableMC"""

from portablemc.standard import Context, Environment
from portablemc.fabric import FabricVersion
from portablemc.auth import MicrosoftAuthSession
from source.pmc.authentication import AuthenticationHandler


class MCManager:
    """MCManager is a class that handles PortableMC."""
    # TODO: Better way of doing this
    auth_session: MicrosoftAuthSession = None
    environment: Environment = None

    def __init__(self, context: tuple[str, str]):
        self.context = Context(*context)

    def provision_version(self) -> FabricVersion:
        """
        Provisions a version for PortableMC.

        Parameters:
        - context (Context): The context for PortableMC.

        Returns:
        - FabricVersion: The version for PortableMC.
        """
        return FabricVersion.with_fabric("1.20.6", context=self.context)

    def authenticate(self, email: str) -> MicrosoftAuthSession:
        """
        Authenticates the user.

        Returns:
        - MicrosoftAuthSession: The Microsoft authentication session.
        """
        auth_handler = AuthenticationHandler(email, self.context)
        auth_session = auth_handler.authenticate()
        MCManager.auth_session = auth_session
        return auth_session
