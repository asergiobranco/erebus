from .server import ErebusServer

server = ErebusServer(
    "0.0.0.0", 8000
)

server.start()