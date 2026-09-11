"""
Umbrella Network - web_server.py

This file provides a safe local web server lab for the Umbrella Network project.

It demonstrates:
- Local HTTP hosting
- Basic web routes
- Request handling
- Browser-based testing
- Safe localhost networking.
"""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from functools import partial
from pathlib import Path

DEFAULT_WEB_HOST = "127.0.0.1"
DEFAULT_WEB_PORT = 8080

def get_web_settings(config):
    """
    Read web server settings from the project config.
    """

    if config is None:
        config = {}

    host = config.get("web_host", DEFAULT_WEB_HOST)
    port = config.get("web_port", DEFAULT_WEB_PORT)

    try:
        port = int(port)
    
    except (TypeError, ValueError):
        print("[!] Invalid web_port in config. Falling back to 8080.")
        port = DEFAULT_WEB_PORT

    return host, port

class UmbrellaWebHandler(SimpleHTTPRequestHandler):
    """
    Handle local web requests for the Umbrella Network web lab.
    """

    def do_GET(self):
        """
        Handle browser GET requests.
        """

        parsed_url = urlparse(self.path)
        path = parsed_url.path

        print(f"[GET] {self.client_address[0]} requested {path}")

        if path == "/health":
            self.send_health_check()
            return
        
        if path == "/about":
            self.path = "/about.html"

        elif path == "/":
            self.path = "/index.html"

        return super().do_GET()
    
    def send_health_check(self):
        """
        Send a simple text health check response.
        """

        message = "Umbrella Network web server is online."

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(message)))
        self.end_headers()
        self.wfile.write(message.encode("utf-8"))

def run_web_server(config=None):
    """
    Start the local Umbrella Network web server.
    """

    host, port = get_web_settings(config)

    server_address = (host, port)

    try:
        web_directory = Path(__file__).resolve().parent

        handler = partial(
            UmbrellaWebHandler,
            directory=str(web_directory)
        )

        web_server = ThreadingHTTPServer(server_address, handler)

        print("[+] Umbrella Network web server started.")
        print(f"[+] Open this in your browser: http://{host}:{port}")
        print("[+] Routes:")
        print("    /")
        print("    /about")
        print("    /health")
        print("[+] Press CTRL+C to stop the server.")

        web_server.serve_forever()

    except KeyboardInterrupt:
        print("\n[!] Web server stopped by user.")
        
    except OSError as error:
        print(f"[!] Could not start the web server: {error}")

    finally:
        try:
            web_server.server_close()
            print("[+] Web server closed.")

        except UnboundLocalError:
            pass     
