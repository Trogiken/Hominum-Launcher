"""
This module contains the AuthenticationHandler class
which is used to authenticate a user with Microsoft's services.

Classes:
- AuthenticationHandler: A class used to authenticate a user with Microsoft's services.

Constants:
- LAUNCHER_NAME: The name of the launcher.
- LAUNCHER_VERSION: The version of the launcher.
- AUTH_DATABASE_FILE_NAME: The name of the authentication database file.
- CLIENT_ID: The client ID.
- APP_ID: The app ID.
- CODE_REDIRECT_URI: The code redirect URI.
- NONCE: The nonce.
"""

import threading
from queue import Queue
import urllib.parse
import webbrowser
from typing import cast
from uuid import uuid4
from http.server import HTTPServer, BaseHTTPRequestHandler
from portablemc.auth import MicrosoftAuthSession, AuthDatabase
from portablemc.standard import Context
from source.path import PROGRAM_NAME, VERSION, APPLICATION_DIR

LAUNCHER_NAME, LAUNCHER_VERSION = PROGRAM_NAME, VERSION
AUTH_DATABASE_FILE_NAME = "portablemc_auth.json"
CLIENT_ID = "2b4ca0d5-a2f0-42bf-aed1-eeafa1139f26"
APP_ID = "2b4ca0d5-a2f0-42bf-aed1-eeafa1139f26"
CODE_REDIRECT_URI = "http://localhost:7969/code"  # URI of your choice
NONCE = uuid4().hex  # random string


# FIXME: When compiled to windowed only, the program doesn't send responses
# TODO: Run servers in separate threads


class AuthenticationHandler:
    """
    A class used to authenticate a user with Microsoft's services.
    
    Methods:
    - __init__: Initializes the AuthenticationHandler instance.
    - gen_auth_url: Generate the authentication URL.
    - run_auth_server: Run the authentication server.
    - microsoft_authenticate: Authenticate the user with Microsoft's services.
    """
    def __init__(self, email: str, context: Context):
        self.email = email
        self.context = context
        self.auth_database = AuthDatabase(self.context.work_dir / AUTH_DATABASE_FILE_NAME)

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
            "state": "port:8690",
            "prompt": "login",
            "response_mode": "fragment"
        })
        return f"https://login.live.com/oauth20_authorize.srf?{ref}"

    # TODO: Private this
    def run_auth_server(self) -> str:
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
                super().__init__(("localhost", 8690), RequestHandler)
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
            print("ID Token:", id_token)
            print("Code:", code)

            if not MicrosoftAuthSession.check_token_id(id_token, self.email, NONCE):
                return None

            return code
        return None

    # TODO: Put this into a run_webserver method and private it like above
    @staticmethod
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
            print(file_path)
            with open(file_path, "r", encoding="utf-8") as f:
                html = f.read()

            # send response
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))

    def microsoft_authenticate(self) -> MicrosoftAuthSession:
        """
        Authenticate the user with Microsoft's services.
        
        Returns:
        - MicrosoftAuthSession: The Microsoft authentication session.
        """
        url = self.gen_auth_url()
        webbrowser.open(url)
        print("Opened browser to", url)

        # Create a Queue object
        q = Queue()

        # Modify the target function to put the result in the queue
        def run_auth_server_and_store_result():
            result = self.run_auth_server()
            q.put(result)

        # run auth server
        auth_server = threading.Thread(target=run_auth_server_and_store_result)
        auth_server.start()

        # Run web server
        server_address = ("", 7969)
        httpd = HTTPServer(server_address, self.WebHandler)
        web_server = threading.Thread(target=httpd.serve_forever)
        web_server.start()

        # Get the result from the queue
        code = q.get()

        if code is None:
            return None

        # TODO: Make sure it stores the session in the correct auth database
        return MicrosoftAuthSession.authenticate(
            self.auth_database.get_client_id(), APP_ID, code, CODE_REDIRECT_URI
        )
