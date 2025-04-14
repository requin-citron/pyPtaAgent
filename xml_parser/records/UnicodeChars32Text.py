from ..records.UnicodeChars8Text import UnicodeChars8TextRecord
import struct

class UnicodeChars32TextRecord(UnicodeChars8TextRecord):
    type = 0xBA

    def to_bytes(self) -> bytes:
        data = self.value.encode('utf-16')[2:]
        bytes = struct.pack('<B', self.type)
        bytes += struct.pack('<I', len(data))
        bytes += data
        return bytes

    def __str__(self):
        return self.value

    @classmethod
    def parse(cls, fp):
        ln = struct.unpack('<I', fp.read(1))[0]
        data = fp.read(ln)
        return cls(data.decode('utf-16'))