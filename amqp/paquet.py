import struct
import io
from enum import Enum, IntEnum

class AMQPProtocol(IntEnum):
    AMQP = 0
    TLS = 2
    SASL = 3

class AMQPMessageType(IntEnum):
    SASLInit = 0x41
    AMQPOpen = 0x10
    AMQPBegin = 0x11
    AMQPAttach = 0x12
    AMQPFlow = 0x13
    AMQPTransfer = 0x14
    AMQPDisposition = 0x15
    AMQPDetach = 0x16
    AMQPEnd = 0x17
    AMQPClose = 0x18

class SASLMechanics(Enum):
    EXTERNAL = "EXTERNAL"
    MSSBCBS = "MSSBCBS"
    PLAIN = "PLAIN"
    ANONYMOUS = "ANONYMOUS"

class AMQPItem:
    def __init__(self):
        self.stream = io.BytesIO()

    def _write(self, data):
        self.stream.write(data)

    def _write_byte(self, byte_val):
        self._write(bytes([byte_val]))

    def _write_byte_array(self, byte_arr):
        self._write(byte_arr)

    def _write_int(self, value, fmt):
        bin_value = struct.pack(f'>{fmt}', value)
        self._write(bin_value)

    def _write_uint32(self, value):
        self._write_int(value, 'I')

    def _get_bytes(self):
        return self.stream.getvalue()

    def to_byte_array(self):
        data = self._get_bytes()
        self.stream.close()
        return data

    def clear_buffer(self):
        self.stream = io.BytesIO()

class AMQPMap(AMQPItem):
    def __init__(self):
        super().__init__()
        self.keys = []
        self.values = []

    def add(self, key, value):
        self.keys.append(key)
        self.values.append(value)

    def to_byte_array(self):
        if not self.keys:
            raise ValueError("Map cannot be empty!")

        entries = bytearray()
        for key, value in zip(self.keys, self.values):
            entries.extend(key.to_byte_array())
            entries.extend(value.to_byte_array())

        num_elements = len(self.keys) * 2
        bin_elements = bytes(entries)

        self.clear_buffer()

        if num_elements < 255 and len(bin_elements) < 255:
            self._write_byte(0xC1)
            self._write_byte(len(bin_elements) + 2)
            self._write_byte(num_elements)
        else:
            self._write_byte(0xD1)
            self._write_uint32(len(bin_elements) + 5)
            self._write_uint32(num_elements)

        self._write_byte_array(bin_elements)
        return self._get_bytes()

class AMQPString(AMQPItem):
    def __init__(self, content):
        super().__init__()
        bin_content = content.encode('utf-8')
        self._write_byte(0xA1 if len(bin_content) < 255 else 0xB1)
        if len(bin_content) < 255:
            self._write_byte(len(bin_content))
        else:
            self._write_int(len(bin_content), 'I')
        self._write_byte_array(bin_content)

class AMQPSymbol(AMQPItem):
    def __init__(self, content):
        super().__init__()
        bin_content = content.encode('ascii')
        self._write_byte(0xA3 if len(bin_content) < 255 else 0xB3)
        if len(bin_content) < 255:
            self._write_byte(len(bin_content))
        else:
            self._write_int(len(bin_content), 'I')
        self._write_byte_array(bin_content)

class AMQPMessage(AMQPItem):
    def __init__(self):
        super().__init__()

    def init(self, msg_type, content):
        message_type = 0
        if msg_type == AMQPMessageType.SASLInit:
            message_type = 1
        bin_content = content.to_byte_array()
        self._write_int(len(bin_content) + 11, 'I')
        self._write_byte(0x02)
        self._write_byte(message_type)
        self._write_byte(0)
        self._write_byte(0)
        self._write_byte(0)
        self._write_byte_array(AMQPSmallULong(msg_type).to_byte_array())
        self._write_byte_array(bin_content)

class AMQPEmpty(AMQPMessage):
    def __init__(self):
        super().__init__()
        self._write_uint32(8)
        self._write_byte(2)
        self._write_byte(0)
        self._write_byte(0)
        self._write_byte(0)

class AMQPNull(AMQPItem):
    def to_byte_array(self):
        return bytes([0x40])

class AMQPTrue(AMQPItem):
    def to_byte_array(self):
        return bytes([0x41])

class AMQPFalse(AMQPItem):
    def to_byte_array(self):
        return bytes([0x42])

class AMQPSmallULong(AMQPItem):
    def __init__(self, value):
        super().__init__()
        if value == 0:
            self._write_byte(0x44)
        else:
            self._write_byte(0x53)
            self._write_byte(value)

class AMQPSmallUInt(AMQPItem):
    def __init__(self, value):
        super().__init__()
        if value == 0:
            self._write_byte(0x43)
        else:
            self._write_byte(0x52)
            self._write_byte(value)

class AMQPUInt(AMQPItem):
    def __init__(self, value):
        super().__init__()
        if value == 0:
            self._write_byte(0x43)
        else:
            self._write_byte(0x70)
            self._write_int(value, 'I')

class AMQPUShort(AMQPItem):
    def __init__(self, value):
        super().__init__()
        self._write_byte(0x60)
        self._write_int(value, 'H')

class AMQPConstructor(AMQPItem):
    def __init__(self, descriptor, value):
        super().__init__()
        self._write_byte(0x00)
        self._write_byte_array(descriptor.to_byte_array())
        self._write_byte_array(value.to_byte_array())