import logging
import ssl
from typing import Optional
from websockets import WebSocketClientProtocol

COLORS = [
    '\033[95m',  # Magenta
    '\033[96m',  # Cyan
    '\033[93m',  # Jaune
    '\033[94m',  # Bleu
    '\033[92m',  # Vert
    '\033[91m',  # Rouge
]

class RelaySettings:
    def __init__(self, parsed: dict, cert_file: str, key_file: str):
        self.host_name = parsed["InstanceDnsAddress"]
        self.relay_id = parsed["Id"]
        self.cert_file = cert_file
        self.key_file = key_file
        self.token = None
        self.socket: Optional[WebSocketClientProtocol] = None
        self.certificate = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.certificate.load_cert_chain(cert_file, key_file)
        self.certificate.check_hostname = False
        self.certificate.verify_mode = ssl.CERT_NONE

    def __str__(self):
        return f"RelaySettings(id={self.relay_id}, host={self.host_name})"

class RelayManager:
    """
    Manages a collection of RelaySettings identified by relay IDs.
    Provides thread-safe methods to add, retrieve, and remove relay settings.
    """

    def __init__(self):
        self.relays: Dict[str, RelaySettings] = {}
        self.lock = asyncio.Lock()

    async def add_relay(self, relay_id: str, settings: RelaySettings):
        async with self.lock:
            if relay_id not in self.relays:
                self.relays[relay_id] = settings
                return True
            return False

    async def get_relay(self, relay_id: str) -> Optional[RelaySettings]:
        async with self.lock:
            return self.relays.get(relay_id)

    async def remove_relay(self, relay_id: str):
        async with self.lock:
            if relay_id in self.relays:
                del self.relays[relay_id]

import asyncio

class RelayWebSocketClient:
    def __init__(
        self,
        settings: RelaySettings,
        thread_id: int = 0,
        logger: logging.Logger = None
    ):
        self.settings = settings
        self.thread_id = str(thread_id)
        self.color = COLORS[int(thread_id) % len(COLORS)]
        self.logger = logger
        self.ws: Optional[websockets.WebSocketClientProtocol] = None

    async def run(self) -> None:
        self.logger.info(f"Starting Relay listener on settings {self.settings}")
        while 1:
            await asyncio.sleep(1)
        # ToDo
        # https://github.com/secureworks/PTAAgentDump/blob/main/PTAAgent.cs#L323-L448