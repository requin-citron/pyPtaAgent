import ssl
from typing import Optional
from websockets import WebSocketClientProtocol
from logger import configure_custom_logger

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


class RelayWebSocketClient:
    def __init__(
        self,
        settings: RelaySettings,
        thread_id: int = 0
    ):
        self.settings = settings
        self.thread_id = str(thread_id)
        self.color = COLORS[thread_id % len(COLORS)]
        self.logger = configure_custom_logger(logs_dir="./logs", color=self.color, thread_id=self.thread_id)
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
    
    async def run(self) -> None:
        print('TODO')
        pass
        # ToDo
        # https://github.com/secureworks/PTAAgentDump/blob/main/PTAAgent.cs#L323-L448