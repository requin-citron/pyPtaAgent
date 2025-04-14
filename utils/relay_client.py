from email.policy import default
import logging
import asyncio
import math
import ssl
from typing import Optional
import websockets

from amqp.relay import RelayInit, RelayedAccept
from amqp.parser import parse_relay_message

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
        self.socket: Optional[websockets.WebSocketClientProtocol] = None
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

    async def connect(self) -> None:
        ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ssl_context.load_cert_chain(certfile=self.settings.cert_file, keyfile=self.settings.key_file)
        self.logger.info(" Tentative de connexion à Azure Service Bus WebSocket...")
        try:
            self.ws = await websockets.connect(
                f"wss://{self.settings.host_name}/$servicebus/websocket",
                subprotocols=["wsrelayedconnection"],
                ssl=ssl_context
            )
            self.logger.info("Connected!")
        except Exception as ex:
            self.logger.error(f"Error while connecting to Relay WebSocket ({type(ex).__name__}): {ex}")
            return False
        return True

    async def send(self, message: bytes, name='packet') -> None:
        if not self.ws:
            self.logger.error("WebSocket connection not established")
            raise RuntimeError("WebSocket connection not established")
        self.logger.debug(f"Sent {name} ({len(message)}): {message.hex()}")
        await self.ws.send(message)

    async def recv(self, name='packet') -> bytes:
        if not self.ws:
            self.logger.error("WebSocket connection not established")
            raise RuntimeError("WebSocket connection not established")
        r = await self.ws.recv()
        self.logger.debug(f"Received {name} ({len(r)}): {r.hex()}")
        return parse_relay_message(r)

    async def setup_connection(self) -> None:
        if not self.ws:
            self.logger.error("WebSocket connection not established")
            raise RuntimeError("WebSocket connection not established")
        
        await self.send(RelayInit().to_byte_array())
        await self.send(RelayedAccept(self.settings.relay_id).to_byte_array())

    async def loop(self):
        try:
            while True:
                parsed = await self.recv()
                print(parsed.to_dict())
                _type = parsed["Type"]
                self.logger.info(f"Received {_type} message")
                match _type:
                    case "RelayResponseError":
                        return
                    case "RelaySB":
                        continue
                    case "Disconnect":
                        return
                    case "CreateSequence":
                        continue
                    case "AckRequested":
                        continue
                    case "SignalConnector":
                        continue
                    case "PasswordValidation":
                        continue
                    case "RelayedAcceptReply":
                        await self.send(bytes([0x0B]))
                    case "RelayResponseOk":
                        continue
                    case "Fault":
                        self.logger.error(f"Received error: {parsed['Reason']}")
                    case _:
                        self.logger.info(f"Skipping {_type} message")
                
                await asyncio.sleep(1)

        except websockets.exceptions.ConnectionClosed:
            self.logger.info("Connection with relay closed by peer")
        except Exception as ex:
            self.logger.error(f"Error in loop ({type(ex).__name__}): {ex}")


    async def run(self) -> None:
        self.logger.info(f"Starting Relay listener on settings {self.settings}")
        if not await self.connect():
            return

        await self.setup_connection()
        await self.loop()