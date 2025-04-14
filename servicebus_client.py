from logger import configure_custom_logger

import websockets, ssl, hashlib, urllib, base64, hmac, uuid, time
from typing import Optional
from amqp import *

# Liste de couleurs ANSI disponibles
COLORS = [
    '\033[95m',  # Magenta
    '\033[96m',  # Cyan
    '\033[93m',  # Jaune
    '\033[94m',  # Bleu
    '\033[92m',  # Vert
    '\033[91m',  # Rouge
]

class ServiceBusWebSocketClient:
    def __init__(
        self,
        namespace: str,
        cert_file: str,
        key_file: str,
        shared_access_key_name: str,
        shared_access_key: str,
        service_path: str,
        thread_id: int = 0
    ):
        self.namespace = namespace
        self.cert_file = cert_file
        self.key_file = key_file
        self.shared_access_key_name = shared_access_key_name
        self.shared_access_key = shared_access_key
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.service_path = service_path
        self.oneway_send_message = 0   
        self.thread_id = str(thread_id)
        self.color = COLORS[thread_id % len(COLORS)]
        self.logger = configure_custom_logger(logs_dir="./logs", color=self.color, thread_id=self.thread_id)
        
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
        return parse_bus_message(r)

    def generate_sas_token(self, uri: str) -> str:
        expiry = str(2320445040)
        string_to_sign = urllib.parse.quote_plus(uri) + "\n" + str(expiry)
        key = self.shared_access_key.encode('utf-8')
        sig = hmac.new(key, string_to_sign.encode('utf-8'), hashlib.sha256).digest()
        signature = base64.b64encode(sig)
        token = "".join([
            "SharedAccessSignature sr=",urllib.parse.quote_plus(uri),
            "&sig=",urllib.parse.quote_plus(signature.decode()),
            "&se=", expiry, 
            "&skn=", self.shared_access_key_name
        ])
        self.logger.info(f"Generated SAS token for {uri}")
        return token

    async def connect(self) -> None:
        ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ssl_context.load_cert_chain(certfile=self.cert_file, keyfile=self.key_file)

        self.logger.info(" Tentative de connexion à Azure Service Bus WebSocket...")
        self.ws = await websockets.connect(
            f"wss://{self.namespace}.servicebus.windows.net/$servicebus/websocket",
            subprotocols=["wsrelayedamqp"],
            ssl=ssl_context
        )
        self.logger.info("Connected!")

    async def setup_connection(self) -> None:
        if not self.ws:
            self.logger.error("WebSocket connection not established")
            raise RuntimeError("WebSocket connection not established")

        relay_link_guid = str(uuid.uuid4())
        tracking_id = str(uuid.uuid4())
        connection_id = str(uuid.uuid4())

        # Step 1: SASL protocol header
        await self.send(AMQPProtocolHeader(AMQPProtocol.SASL).to_byte_array(), 'SASL protocol header')
        await self.recv('SASL response 1')
        await self.recv('SASL response 2')

        # Step 2: SASL Init
        await self.send(SASLInit(SASLMechanics.EXTERNAL).to_byte_array(), 'SASL Init')
        await self.recv('SASL response 3')

        # Step 3: AMQP protocol header
        await self.send(AMQPProtocolHeader(AMQPProtocol.AMQP).to_byte_array(), 'AMQP protocol header')
        await self.recv('AMQP response 1')

        # Step 4: AMQP Open
        await self.send(AMQPOpen(f"RelayConnection_{connection_id}", f"{self.namespace}-relay.servicebus.windows.net").to_byte_array(), 'AMQP Open')
        r = await self.recv('AMQP Open response')
        container_id = r['ContainerId']
        self.logger.info(f"Container ID: {container_id}")

        # Step 5: AMQP Begin
        await self.send(AMQPBegin().to_byte_array(), 'AMQP Begin')
        await self.recv('AMQP Begin response')

        handleIn, handleOut = 0, 1
        link = f"RelayLink_{relay_link_guid}:out"
        sbUrl = f"sb://{self.namespace}.servicebus.windows.net/{self.service_path}/"
        sasUrl = f"http://{self.namespace}.servicebus.windows.net/{self.service_path}/"
        sas = self.generate_sas_token(sasUrl)

        # Step 6: AMQP Attach (in)
        await self.send(AMQPAttach(link, sbUrl, sas, tracking_id, False, handleIn).to_byte_array(), 'AMQP Attach (in)')
        await self.recv('AMQP Attach (in) response')
        
        # Step 7: AMQP Attach (out)
        link = f"RelayLink_{relay_link_guid}:in"
        await self.send(AMQPAttach(link, sbUrl, sas, tracking_id, True, handleOut).to_byte_array(), 'AMQP Attach (out)')
        await self.recv('AMQP Attach (out) response')
        
        # Step 8: AMQP Flow (in)
        await self.send(AMQPFlow(handleIn).to_byte_array(), 'AMQP Flow (in)')
        
        # Step 9: AMQP Flow (out)
        await self.send(AMQPFlow(handleOut).to_byte_array(), 'AMQP Flow (out)')

    async def loop(self) -> None:
        relays = dict()
        try:
            while True:
                await self.send(AMQPEmpty().to_byte_array(), 'AMQP Empty')
                parsed = await self.recv('AMQP response')
                print(parsed.to_dict())

                if parsed['Type'] is None:
                    continue

                match parsed['Type']:
                    case 'AMQP Flow':
                        pass
                    case 'AMQP Attach':
                        pass
                    case 'AMQP Detach':
                        pass
                    case 'AMQP Transfer':
                        pass
                        # logger.critical(f"AMQP Transfer {'='*30}")
                        # if parsed['Size'] > len(buffer):
                        #     key, pos      = parse_amqp_item(await self.ws.recv(), 0)
                        #     oneway_send_key = 0x75
                        #     logger.warning("Received rawContent: "+'\n'+str(key)+str(pos))

                        #     if key.get(oneway_send_key) is not None:
                        #         disposition = AMQPDisposition(True, 0x24, self.oneway_send_message).to_byte_array()
                        #         logger.info(f"Sending AMQP Disposition({len(disposition)}): {disposition.hex()}")
                        #         await self.ws.send(disposition)
                        #         self.oneway_send_message += 1

                        #         bin_oneway_send = key.get(oneway_send_key)
                        #         logger.warning("parse_relay_binary_xml")
                        #         oneway_send = parse_relay_binary_xml(bin_oneway_send, 0, True)

                        #         host_name = oneway_send["InstanceDnsAddress"]
                        #         relay_id  = oneway_send["Id"]

                        #         new_connection = True

                        #         if relays.get(relay_id) is not None:
                        #             raise Exception("Not Imp")
                                
                        #         if new_connection:
                        #             relays[relay_id] = RelaySettings(oneway_send, self.cert_file, self.key_file)
                        #             logger.warning(f"start_relay_listener {'#'*30}")
                        #             asyncio.gather(self.start_relay_listener(relays[relay_id]))
                        #             # new Thread(StartRelayListener).Start(rs);
                        #     else:
                        #         logger.warning("Wrong key in AMQP Transfer packet")
                            
                    case _:
                        self.logger.info(f"Unknown message type: {parsed['Type']}")
                        continue
                time.sleep(1)
        except Exception as e:
            self.logger.error(e)
            
    async def run(self, thread_id: int) -> None:
        self.logger.info(f"Connecting with thread N°{thread_id}")
        await self.connect()

        self.logger.info(f"Initializing connection with thread N°{thread_id}")
        await self.setup_connection()

        self.logger.info(f"Looping with thread N°{thread_id}")
        await self.loop()
        self.logger.info("Ended with thread N°{thread_id}")