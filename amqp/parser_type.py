from typing import Union
import struct, datetime

class ParsedMessage:
    def __init__(self, message_bytes: bytes):
        self.message_bytes = message_bytes
        self.info = {}

    def add(self, key: str, value: Union[str, int, bytes]):
        self.info[key] = value

    def __getitem__(self, key):
        return self.info.get(key)

    def __setitem__(self, key, value):
        self.info[key] = value

    def __str__(self):
        return "\n".join(f"{key} → {value}" for key, value in self.info.items())

    def __repr__(self) -> str:
        return self.__str__()

    def to_dict(self) -> dict:
        return dict(self.info)

def parse_amqp_item(bytes_data, pos):
    p = pos
    ret_val = None
    item_type = bytes_data[p]
    p += 1
    match item_type:
        case 0x00:
            descriptor, p = parse_amqp_item(bytes_data, p)
            value, p = parse_amqp_item(bytes_data, p)
            ret_val = {descriptor: value}

        case 0x40:
            pos = p
        case 0x41:  # True
            ret_val = True

        case 0x42:  # False
            ret_val = False

        case 0x43 | 0x44:  # uint 0 or ulong 0
            ret_val = 0

        case 0x45:  # Empty list
            ret_val = []

        case 0x56:  # Boolean
            ret_val = (bytes_data[p] == 0x01)
            p += 1

        case 0x50 | 0x51 | 0x52 | 0x53:  # ubyte, byte, smalluint, smallulong
            ret_val = bytes_data[p]
            p += 1

        case 0x54:  # smallint
            ret_val = int(bytes_data[p])
            p += 1

        case 0x55:  # smalllong
            ret_val = int(bytes_data[p])
            p += 1

        case 0x60:  # ushort
            ret_val = struct.unpack_from('>H', bytes_data, p)[0]
            p += 2

        case 0x61:  # short
            ret_val = struct.unpack_from('>h', bytes_data, p)[0]
            p += 2

        case 0x70:  # uint
            ret_val = struct.unpack_from('>I', bytes_data, p)[0]
            p += 4

        case 0x71:  # int
            ret_val = struct.unpack_from('>i', bytes_data, p)[0]
            p += 4

        case 0x72:  # float
            ret_val = struct.unpack_from('>f', bytes_data, p)[0]
            p += 4

        case 0x73:  # char
            ret_val = bytes_data[p:p+4][::-1]
            p += 4

        case 0x74: # Do Nothing
            p += 4

        case 0x80:  # ulong
            ret_val = struct.unpack_from('>Q', bytes_data, p)[0]
            p += 8

        case 0x81:  # long
            ret_val = struct.unpack_from('>q', bytes_data, p)[0]
            p += 8

        case 0x82:  # double
            ret_val = struct.unpack_from('>d', bytes_data, p)[0]
            p += 8

        case 0x83:  # timestamp
            timestamp = struct.unpack_from('>Q', bytes_data, p)[0]
            ret_val = datetime.datetime.utcfromtimestamp(timestamp)
            p += 8

        case 0x84: # Do nothing
            p += 8

        case 0x85: # Do nothing
            p += 16

        case 0x98:  # UUID
            uuid_bytes = struct.unpack_from('>16s', bytes_data, p)[0]
            ret_val = uuid_bytes.hex()
            p += 16

        case 0xa0:  # Binary
            length = bytes_data[p]
            p += 1
            ret_val = bytes_data[p:p + length]
            p += length

        case 0xa1:  # String (UTF-8)
            length = bytes_data[p]
            p += 1
            ret_val = bytes_data[p:p + length].decode('utf-8')
            p += length

        case 0xa3:  # Symbol (ASCII)
            length = bytes_data[p]
            p += 1
            ret_val = bytes_data[p:p + length].decode('ascii')
            p += length

        case 0xb0:  # Long Binary
            length = struct.unpack_from('>I', bytes_data, p)[0]
            p += 4
            ret_val = bytes_data[p:p + length]
            p += length

        case 0xb1:  # Long String (ASCII)
            length = struct.unpack_from('>I', bytes_data, p)[0]
            p += 4
            ret_val = bytes_data[p:p + length].decode('ascii')
            p += length

        case 0xb3:  # Long Symbol
            length = struct.unpack_from('>I', bytes_data, p)[0]
            p += 4
            ret_val = bytes_data[p:p + length].decode('ascii')
            p += length
        
        case 0xC0 | 0xD0:  # List
            ret_val, p = parse_amqp_list(bytes_data, p)

        case 0xC1 | 0xD1:  # Map
            ret_val, p = parse_amqp_map(bytes_data, p)

        case 0xE0 | 0xF0:  # Array
            ret_val, p = parse_amqp_array(bytes_data, p)

        case _:  # Default case
            raise ValueError(f"Unhandled item type: {item_type}")
    
    pos = p
    return ret_val, pos

def parse_multi_byte_int31(message_bytes: bytes, offset:int) -> tuple[int,int]:
    i       = 0
    ret_val = 0
    index   = 0
    while i< len(message_bytes):
        num      = message_bytes[offset]
        ret_val |= ( (num & 127) << (index*7) )
        offset += 1
        i      += 1
        if index == 4 and (num&248) != 0:
            raise Exception("Invalid Size")        
        index +=1
        if (num&128) == 0:
            break
    return ret_val, offset


def parse_descriptor(bytes_data, pos):
    descriptor, pos = parse_amqp_item(bytes_data, pos)
    value, pos = parse_amqp_item(bytes_data, pos)
    return {descriptor: value}

def parse_amqp_list(bytes_data, pos):
    ret_val = []
    p = pos - 1
    size = 0
    int_size = 0
    list_type = bytes_data[p]
    p += 1
    if list_type == 0x45:
        return ret_val
    elif list_type == 0xC0:
        p += 1
        size = bytes_data[p-1]
        int_size = 1
    elif list_type == 0xD0:
        size = struct.unpack_from('>I', bytes_data, p)[0]
        p += 4
        int_size = 4

    max_pos = p + size
    p += int_size
    while p < max_pos:
        item, p = parse_amqp_item(bytes_data, p)
        ret_val.append(item)

    pos = p
    return ret_val, pos

def parse_amqp_map(bytes_data, pos):
    ret_val = {}
    p = pos - 1
    size = 0
    int_size = 0
    map_type = bytes_data[p]
    p += 1
    if map_type == 0xC1:
        size = bytes_data[p]
        p += 1
        int_size = 1
    elif map_type == 0xD1:
        size = struct.unpack_from('>I', bytes_data, p)[0]
        p += 4
        int_size = 4

    max_pos = p + size
    p += int_size
    while p < max_pos:
        key, p = parse_amqp_item(bytes_data, p)
        value, p = parse_amqp_item(bytes_data, p)
        ret_val[key] = value

    return ret_val, p

def parse_amqp_array(bytes_data, pos):
    ret_val = []
    p = pos
    size = bytes_data[p]
    p += 1
    elements = bytes_data[p]
    p += 1
    item_type = bytes_data[p]
    p += 1
    for _ in range(elements):
        bytes_data[p - 1] = item_type
        item, p = parse_amqp_item(bytes_data, p - 1)
        ret_val.append(item)
    return ret_val, p

def parse_multibyte_int31(bytes_data, p):
    i = 0
    ret_val = 0
    index = 0
    while i < len(bytes_data):
        num = bytes_data[p]
        ret_val |= (num & 127) << (index * 7)
        p += 1
        i += 1
        if index == 4 and (num & 248) != 0:
            raise Exception("Invalid size")
        index += 1
        if (num & 128) == 0:
            break
    return ret_val, p