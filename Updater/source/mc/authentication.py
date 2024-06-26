"""
A module used to authenticate a user with Microsoft's services.

Classes:
- AuthenticationHandler: A class used to authenticate a user with Microsoft's services.

Constants:
- AUTH_DATABASE_FILE_NAME (str): The name of the authentication database file.
- CLIENT_ID (str): The client ID.
- APP_ID (str): The app ID.
- AUTH_SERVER_PORT (int): The port of the authentication server.
- WEB_SERVER_PORT (int): The port of the web server.
- CODE_REDIRECT_URI (str): The code redirect URI.
- NONCE (str): The nonce.
"""

import threading
from queue import Queue
import urllib.parse
import webbrowser
from typing import cast
from uuid import uuid4
from http.server import HTTPServer, BaseHTTPRequestHandler
from portablemc.http import HttpError
from portablemc.auth import MicrosoftAuthSession, AuthDatabase, AuthError
from portablemc.standard import Context
from source.path import APPLICATION_DIR

AUTH_DATABASE_FILE_NAME = "portablemc_auth.json"  # Authentication database file name
CLIENT_ID = "2b4ca0d5-a2f0-42bf-aed1-eeafa1139f26"  # Same as APP_ID
APP_ID = "2b4ca0d5-a2f0-42bf-aed1-eeafa1139f26"  # Application ID registered in Entra
AUTH_SERVER_PORT = 8690  # Port of the authentication server
WEB_SERVER_PORT = 7969  # Port of the web server
CODE_REDIRECT_URI = "http://localhost:7969/code"  # URI registered in Entra
NONCE = uuid4().hex  # Random string for security


class AuthenticationHandler:
    """
    A class used to authenticate a user with Microsoft's services.
    
    Methods:
    - gen_auth_url: Generate the authentication URL.
    - refresh_session: Refresh the authentication session.
    - authenticate: Authenticate the user with Microsoft's services.
    """
    def __init__(self, email: str, context: Context):
        self.email = email
        self.context = context
        self.auth_database = AuthDatabase(self.context.work_dir / AUTH_DATABASE_FILE_NAME)

    # TODO: Private this
    def _run_auth_server(self) -> str:
        """
        Run the authentication server.
        
        Returns:
        - str: The code.
        """
        class AuthServer(HTTPServer):
            """
            The authentication server.
            
            Methods:
            - __init__: Initializes the AuthServer instance.
            """
            def __init__(self):
                super().__init__(("localhost", AUTH_SERVER_PORT), RequestHandler)
                self.timeout = 0.5
                self.ms_auth_query = None

        class RequestHandler(BaseHTTPRequestHandler):
            """
            The request handler for the authentication server.
            
            Methods:
            - do_GET: Handles the GET request.
            """
            def do_GET(self):
                """
                Handles the GET request.
                
                Sends a response with the access-control-allow-origin header.
                
                Returns:
                - None
                """
                parsed = urllib.parse.urlparse(self.path)
                if parsed.path in ("", "/"):
                    cast(AuthServer, self.server).ms_auth_query = parsed.query
                    self.send_response(200)
                else:
                    self.send_response(404)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.flush()

        # Run the server and handle incoming requests
        with AuthServer() as server:
            try:
                while server.ms_auth_query is None:
                    server.handle_request()
            except KeyboardInterrupt:
                pass

            if server.ms_auth_query is None:
                return None

            auth_query = server.ms_auth_query

        qs = urllib.parse.parse_qs(auth_query)

        if "code" in qs and "id_token" in qs:

            id_token = qs["id_token"][0]
            code = qs["code"][0]

            if not MicrosoftAuthSession.check_token_id(id_token, self.email, NONCE):
                return None

            return code
        return None

    def _run_web_server(self):
        """
        Run the web server in a separate thread.
        """
        class WebHandler(BaseHTTPRequestHandler):
            """
            The web handler for the web server.
            
            Methods:
            - do_GET: Handles the GET request.
            """
            def do_GET(self):
                """
                Handles the GET request.
                
                Sends a response with the content-type header set to text/html.
                """
                # read html file
                file_path = APPLICATION_DIR / "assets" / "resp.html"
                with open(file_path, "r", encoding="utf-8") as f:
                    html = f.read()

                # send response
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(html.encode("utf-8"))
        
        server_address = ("", WEB_SERVER_PORT)
        httpd = HTTPServer(server_address, WebHandler)
        web_server = threading.Thread(target=httpd.serve_forever)
        web_server.start()
        return httpd, web_server

    def gen_auth_url(self) -> str:
        """
        Generate the authentication URL.

        Returns:
        - str: The authentication URL.
        """
        ref = urllib.parse.urlencode({
            "client_id": APP_ID,
            "redirect_uri": CODE_REDIRECT_URI,
            "response_type": "code id_token",
            "scope": "xboxlive.signin offline_access openid email",
            "login_hint": self.email,
            "nonce": NONCE,
            "state": f"port:{AUTH_SERVER_PORT}",
            "prompt": "login",
            "response_mode": "fragment"
        })
        return f"https://login.live.com/oauth20_authorize.srf?{ref}"

    def gen_logout_url(self) -> str:
        """
        Generate the logout URL.
        
        Note: This is not currently possible due to Entra not supporting http for logout redirects.
        
        Returns:
        - str: The logout URL.
        """
        ref = urllib.parse.urlencode({
            "client_id": APP_ID,
            "redirect_uri": CODE_REDIRECT_URI
        })
        return f"https://login.live.com/oauth20_logout.srf?{ref}"

    def get_player_data(self) -> dict:
        """
        Get the player data.

        Returns:
        - dict: The player data.
        """
        raise NotImplementedError

    def refresh_session(self) -> MicrosoftAuthSession:
        """
        Refresh the authentication session.

        Returns:
        - MicrosoftAuthSession: The Microsoft authentication session.
        - None: If the session is invalid or non-existent.
        """
        self.auth_database.load()
        session = self.auth_database.get(self.email, MicrosoftAuthSession)
        if session is None:
            return None
        try:
            if not session.validate():
                session.refresh()
                self.auth_database.save()
            return session
        except (AuthError, HttpError):
            return None

    def remove_session(self):
        """
        Remove the authentication session.
        """
        self.auth_database.load()
        self.auth_database.remove(self.email, MicrosoftAuthSession)
        self.auth_database.save()

    def authenticate(self) -> MicrosoftAuthSession:
        """
        Authenticate the user with Microsoft's services.
        
        Returns:
        - MicrosoftAuthSession: The Microsoft authentication session.
        - None: If the session could not be authenticated.
        """
        session = self.refresh_session()
        if session is not None:
            return session

        url = self.gen_auth_url()
        webbrowser.open(url)

        # Create a Queue object
        q = Queue()

        # Modify the target function to put the result in the queue
        def _run_auth_server_and_store_result():
            result = self._run_auth_server()
            q.put(result)

        # run auth server
        auth_server = threading.Thread(target=_run_auth_server_and_store_result)
        auth_server.start()

        # Run web server
        httpd, web_server = self._run_web_server()

        # Get the result from the queue
        code = q.get()

        httpd.shutdown()
        web_server.join()
        auth_server.join()

        if code is None:
            return None

        # TODO: Add error handling here
        session = MicrosoftAuthSession.authenticate(
            self.auth_database.get_client_id(), APP_ID, code, CODE_REDIRECT_URI
        )

        if session is None:
            return None

        self.auth_database.put(self.email, session)
        self.auth_database.save()

        return session
