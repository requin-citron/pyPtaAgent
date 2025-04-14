from io import BytesIO
from xml.etree import ElementTree as ET
from typing import Optional, List

from amqp.paquet import AMQPItem

class RelayMessage(AMQPItem):
    @staticmethod
    def int_to_multibyte_int32(value: int) -> bytes:
        if value < 0:
            raise ValueError("Value must be non-negative")
        tmp_val = value
        size = 1
        while tmp_val & 0x80 != 0:
            size += 1
            tmp_val >>= 7
        bytes_array = bytearray(size)
        offset = 0
        while value & 0x80 != 0:
            bytes_array[offset] = (value & 0x7F) | 0x80
            value >>= 7
            offset += 1
        bytes_array[offset] = value
        return bytes(bytes_array)
    
    def __init__(self):
        super().__init__()
        self.service_model_strings = [""]
    
    def get_session_string_array(self, strings: Optional[List[str]] = None) -> Optional[bytes]:
        if strings is None:
            return None

        byte_strings = []
        for ses_str in strings:
            value = ses_str or ""
            utf8_string = value.encode('utf-8')
            byte_strings.append(self.int_to_multibyte_int32(len(utf8_string)))
            byte_strings.append(utf8_string)

        return b''.join(byte_strings)

    def write_xml(self, xml: str) -> None:
        pass

class RelayInit(RelayMessage):
    def __init__(self):
        super().__init__()
        self._write_byte(0x1e)
        self._write_byte(0x01)
        self._write_byte(0x00)
        self._write_byte(0x00)

class RelayedAccept(RelayMessage):
    def __init__(self, relay_id: str):
        super().__init__()
        """
        <s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" xmlns:a="http://www.w3.org/2005/08/addressing">
            <s:Header>
                <a:Action s:mustUnderstand="1">RelayedAccept</a:Action>
                <a:To s:mustUnderstand="1">http://schemas.microsoft.com/2005/12/ServiceModel/Addressing/Anonymous</a:To>
            </s:Header>
            <s:Body>
                <RelayedAccept xmlns="http://schemas.microsoft.com/netservices/2009/05/servicebus/connect" xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
                    <Id>{0}</Id>
                </RelayedAccept>
            </s:Body>
        </s:Envelope>
        """
        self._write_byte_array(bytes([
            0x56, 0x02, 0x0B, 0x01, 0x73, 0x04, 0x0B, 0x01, 0x61, 0x06,
            0x56, 0x08, 0x44, 0x0A, 0x1E, 0x00, 0x82, 0x99, 0x0D, 0x52, 0x65,
            0x6C, 0x61, 0x79, 0x65, 0x64, 0x41, 0x63, 0x63, 0x65, 0x70, 0x74,
            0x44, 0x0C, 0x1E, 0x00, 0x82, 0x99, 0x46, 0x68, 0x74, 0x74, 0x70,
            0x3A, 0x2F, 0x2F, 0x73, 0x63, 0x68, 0x65, 0x6D, 0x61, 0x73, 0x2E,
            0x6D, 0x69, 0x63, 0x72, 0x6F, 0x73, 0x6F, 0x66, 0x74, 0x2E, 0x63,
            0x6F, 0x6D, 0x2F, 0x32, 0x30, 0x30, 0x35, 0x2F, 0x31, 0x32, 0x2F,
            0x53, 0x65, 0x72, 0x76, 0x69, 0x63, 0x65, 0x4D, 0x6F, 0x64, 0x65,
            0x6C, 0x2F, 0x41, 0x64, 0x64, 0x72, 0x65, 0x73, 0x73, 0x69, 0x6E,
            0x67, 0x2F, 0x41, 0x6E, 0x6F, 0x6E, 0x79, 0x6D, 0x6F, 0x75, 0x73,
            0x01, 0x56, 0x0E, 0x40, 0x0D, 0x52, 0x65, 0x6C, 0x61, 0x79, 0x65,
            0x64, 0x41, 0x63, 0x63, 0x65, 0x70, 0x74, 0x08, 0x43, 0x68, 0x74,
            0x74, 0x70, 0x3A, 0x2F, 0x2F, 0x73, 0x63, 0x68, 0x65, 0x6D, 0x61,
            0x73, 0x2E, 0x6D, 0x69, 0x63, 0x72, 0x6F, 0x73, 0x6F, 0x66, 0x74,
            0x2E, 0x63, 0x6F, 0x6D, 0x2F, 0x6E, 0x65, 0x74, 0x73, 0x65, 0x72,
            0x76, 0x69, 0x63, 0x65, 0x73, 0x2F, 0x32, 0x30, 0x30, 0x39, 0x2F,
            0x30, 0x35, 0x2F, 0x73, 0x65, 0x72, 0x76, 0x69, 0x63, 0x65, 0x62,
            0x75, 0x73, 0x2F, 0x63, 0x6F, 0x6E, 0x6E, 0x65, 0x63, 0x74, 0x09,
            0x01, 0x69, 0x29, 0x68, 0x74, 0x74, 0x70, 0x3A, 0x2F, 0x2F, 0x77,
            0x77, 0x77, 0x2E, 0x77, 0x33, 0x2E, 0x6F, 0x72, 0x67, 0x2F, 0x32,
            0x30, 0x30, 0x31, 0x2F, 0x58, 0x4D, 0x4C, 0x53, 0x63, 0x68, 0x65,
            0x6D, 0x61, 0x2D, 0x69, 0x6E, 0x73, 0x74, 0x61, 0x6E, 0x63, 0x65,
            0x40, 0x02, 0x49, 0x64, 0x99, 0x24
        ]))
        self._write_byte_array(relay_id.encode('utf-8'))
        self._write_byte_array(bytes([0x01, 0x01, 0x01]))

class CreateSequenceResponse(RelayMessage):
    def __init__(self, relates_to: str, id: str, service_bus: str):
        super().__init__()
        self._xml = f"""
        <s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" xmlns:a="http://www.w3.org/2005/08/addressing">
            <s:Header>
                <a:Action s:mustUnderstand="1">http://schemas.xmlsoap.org/ws/2005/02/rm/CreateSequenceResponse</a:Action>
                <a:RelatesTo>urn:uuid:{relates_to}</a:RelatesTo>
                <a:To s:mustUnderstand="1">http://www.w3.org/2005/08/addressing/anonymous</a:To>
            </s:Header>
            <s:Body>
                <CreateSequenceResponse xmlns="http://schemas.xmlsoap.org/ws/2005/02/rm">
                    <Identifier>urn:uuid:{id}</Identifier>
                    <Accept>
                        <AcksTo>
                            <a:Address>{service_bus}</a:Address>
                        </AcksTo>
                    </Accept>
                </CreateSequenceResponse>
            </s:Body>
        </s:Envelope>
        """
        self._build_message(relates_to, id, service_bus)

    @property
    def xml(self) -> str:
        return self._xml

    def _build_message(self, relates_to: str, id: str, service_bus: str) -> None:
        relates_to_bytes = bytes.fromhex(relates_to.replace('-', ''))
        id_bytes = bytes.fromhex(id.replace('-', ''))
        service_bus_bytes = service_bus.encode('utf-8')
        content = bytearray([
            0x56, 0x02, 0x0B, 0x01, 0x73, 0x04, 0x0B, 0x01, 0x61, 0x06,
            0x56, 0x08, 0x44, 0x0A, 0x1E, 0x00, 0x82, 0xAB, 0xA0, 0x05, 0x44,
            0x12, 0xAD
        ])        
        content.extend(relates_to_bytes)
        content.extend([
            0x44, 0x0C, 0x1E, 0x00, 0x82, 0xAB, 0x14, 0x01, 0x56, 0x0E, 0x42,
            0x9E, 0x05, 0x0A, 0x20, 0x42, 0x1E, 0xAD
        ])
        content.extend(id_bytes)
        content.extend([
            0x42, 0x96, 0x05, 0x42, 0x94, 0x05, 0x44, 0x2A, 0x99
        ])
        content.extend(self.int_to_multibyte_int32(len(service_bus_bytes)))
        content.extend(service_bus_bytes)
        content.extend([0x01, 0x01, 0x01, 0x01, 0x01])
        self._write_byte(0x06)                                                 # Message type
        self._write_byte_array(self.int_to_multibyte_int32(len(content) + 1))  # Message length
        self._write_byte_array(self.int_to_multibyte_int32(0x00))              # SessionStrings length
        self._write_byte_array(content)


class SignalConnectorResponse(RelayMessage):
    _service_model_strings = [
        "http://tempuri.org/IConnectorSignalingService/SignalConnectorResponse",
        "SignalConnectorResponse",
        "http://tempuri.org/",
        "SignalConnectorResult",
        "http://schemas.datacontract.org/2004/07/Microsoft.ApplicationProxy.Common.SignalingDataModel",
        "http://www.w3.org/2001/XMLSchema-instance",
        "AckLatency",
        "ConnectorId"
    ]
    
    def __init__(self, relates_to: str, id: str, connector_id: str):
        super().__init__()
        sequence = ""
        if id != "00000000-0000-0000-0000-000000000000":
            sequence = f"""
            <r:Sequence s:mustUnderstand="1">
                <r:Identifier>urn:uuid:{id}</r:Identifier>
                <r:MessageNumber>1</r:MessageNumber>
            </r:Sequence>
            """
        
        self._xml = f"""
        <s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" xmlns:r="http://schemas.xmlsoap.org/ws/2005/02/rm" xmlns:a="http://www.w3.org/2005/08/addressing">
            <s:Header>
                <r:AckRequested>
                    <r:Identifier>urn:uuid:{relates_to}</r:Identifier>
                </r:AckRequested>
                {sequence}
                <a:Action s:mustUnderstand="1">http://tempuri.org/IConnectorSignalingService/SignalConnectorResponse</a:Action>
                <a:RelatesTo>urn:uuid:{relates_to}</a:RelatesTo>
                <a:To s:mustUnderstand="1">http://www.w3.org/2005/08/addressing/anonymous</a:To>
            </s:Header>
            <s:Body>
                <SignalConnectorResponse xmlns="http://tempuri.org/">
                    <SignalConnectorResult xmlns:b="http://schemas.datacontract.org/2004/07/Microsoft.ApplicationProxy.Common.SignalingDataModel" xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
                        <b:AckLatency>0</b:AckLatency>
                        <b:ConnectorId>{connector_id}</b:ConnectorId>
                    </SignalConnectorResult>
                </SignalConnectorResponse>
            </s:Body>
        </s:Envelope>
        """
        self._build_message(relates_to, id, connector_id)

    @property
    def xml(self) -> str:
        return self._xml

    def _build_message(self, relates_to: str, id: str, connector_id: str) -> None:
        relates_to_bytes = bytes.fromhex(relates_to.replace('-', ''))
        id_bytes = bytes.fromhex(id.replace('-', ''))
        content = bytearray([
            0x56, 0x02, 0x0B, 0x01, 0x73, 0x04, 0x0B, 0x01, 0x72, 0x20, 0x0B, 0x01, 0x61, 0x06,
            0x56, 0x08, 0x55, 0x90, 0x05, 0x55, 0x1E, 0xAD
        ])
        content.extend(id_bytes)
        content.extend([
            0x01, 0x55, 0x3E, 0x1E, 0x00, 0x82, 0x55, 0x1E, 0xAD
        ])
        content.extend(id_bytes)
        content.extend([
            0x55, 0x40, 0x83, 0x01, 0x44, 0x0A, 0x1E, 0x00, 0x82, 0xAB, 0x01, 0x44, 0x12, 0xAD
        ])        
        content.extend(relates_to_bytes)
        content.extend([
            0x44, 0x0C, 0x1E, 0x00, 0x82, 0xAB, 0x14, 0x01, 0x56, 0x0E, 0x42, 0x03, 0x0A, 0x05,
            0x42, 0x07, 0x0B, 0x01, 0x62, 0x09, 0x0B, 0x01, 0x69, 0x0B, 0x45, 0x0D, 0x81, 0x45,
            0x0F, 0x99
        ])
        connector_id_bytes = connector_id.encode('utf-8')
        content.extend(self.int_to_multibyte_int32(len(connector_id_bytes)))
        content.extend(connector_id_bytes)
        content.extend([0x01, 0x01, 0x01, 0x01])
        session_strings = self.get_session_string_array(self._service_model_strings)
        session_string_len = self.int_to_multibyte_int32(len(session_strings)) if session_strings else self.int_to_multibyte_int32(0)
        
        # Message header
        self._write_byte(0x06)  # Message type
        self._write_byte_array(self.int_to_multibyte_int32(len(content) + len(session_string_len) + len(session_strings) if session_strings else 0))  # Message length
        self._write_byte_array(session_string_len)  # Session strings length
        if session_strings:
            self._write_byte_array(session_strings)  # Session strings
        
        self._write_byte_array(content)

class SequenceAcknowledgement(RelayMessage):
    def __init__(self, id: str):
        super().__init__()
        self._xml = f"""
        <s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" xmlns:r="http://schemas.xmlsoap.org/ws/2005/02/rm" xmlns:a="http://www.w3.org/2005/08/addressing">
            <s:Header>
                <r:SequenceAcknowledgement>
                    <r:Identifier>urn:uuid:{id}</r:Identifier>
                    <r:AcknowledgementRange Lower="1" Upper="1"/>
                    <netrm:BufferRemaining xmlns:netrm="http://schemas.microsoft.com/ws/2006/05/rm">8</netrm:BufferRemaining>
                </r:SequenceAcknowledgement>
                <a:Action s:mustUnderstand="1">http://schemas.xmlsoap.org/ws/2005/02/rm/SequenceAcknowledgement</a:Action>
                <a:To s:mustUnderstand="1">http://www.w3.org/2005/08/addressing/anonymous</a:To>
            </s:Header>
            <s:Body/>
        </s:Envelope>
        """
        self._build_message(id)

    @property
    def xml(self) -> str:
        return self._xml

    def _build_message(self, id: str) -> None:
        id_bytes = bytes.fromhex(id.replace('-', ''))
        content = bytearray([
            0x56, 0x02, 0x0B, 0x01, 0x73, 0x04, 0x0B, 0x01, 0x72, 0x20, 0x0B, 0x01, 0x61, 0x06,
            0x56, 0x08, 0x55, 0x2E, 0x55, 0x1E, 0xAD
        ])
        content.extend(id_bytes)
        content.extend([
            0x55, 0x30, 0x06, 0x34, 0x82, 0x06, 0x32, 0x82, 0x01, 0x43, 0x05, 0x6E, 0x65, 0x74,
            0x72, 0x6D, 0x36, 0x0B, 0x05, 0x6E, 0x65, 0x74, 0x72, 0x6D, 0x38, 0x89, 0x08, 0x01,
            0x44, 0x0A, 0x1E, 0x00, 0x82, 0xAB, 0x3A, 0x44, 0x0C, 0x1E, 0x00, 0x82, 0xAB, 0x14,
            0x01, 0x56, 0x0E, 0x01, 0x01
        ])
        self._write_byte(0x06)  # Message type
        self._write_byte_array(self.int_to_multibyte_int32(len(content) + 1))  # Message length
        self._write_byte_array(self.int_to_multibyte_int32(0))  # Session strings length
        self._write_byte_array(content)