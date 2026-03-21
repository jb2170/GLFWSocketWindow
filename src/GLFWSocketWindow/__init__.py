"""
GLFW window that listens on a UNIX socket for a stream of RGBA pixels
""".removeprefix("\n")

__version__ = "0.0.2"

import os
import argparse
import socketserver

from .GLFWWindow import GLFWWindow

class Handler(socketserver.BaseRequestHandler):
    window = None

    def setup(self):
        print("Client connect")
        self.request.setblocking(False)

    def handle(self):
        window = self.window
        sock = self.request

        window.main(sock)

    def finish(self):
        print("Client exit")

class Server(socketserver.UnixStreamServer):
    def service_actions(self):
        window = Handler.window

        window.raise_for_close()
        window.poll_events()

def get_cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description = __doc__)

    parser.add_argument("socket_path", metavar = "SOCKET")
    parser.add_argument(
        "--width", metavar = "WIDTH", dest = "window_width",
        type = int, default = 640
    )
    parser.add_argument(
        "--height", metavar = "HEIGHT", dest = "window_height",
        type = int, default = 480
    )

    args = parser.parse_args()

    return args

def main() -> None:
    args = get_cli_args()

    server_address = args.socket_path
    window_width   = args.window_width
    window_height  = args.window_height

    window = GLFWWindow(window_width, window_height)

    Handler.window = window

    server = Server(server_address, Handler)

    with server, window:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass

    try:
        os.unlink(server_address)
    except Exception:
        pass
