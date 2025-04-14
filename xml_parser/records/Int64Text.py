from ..records.Int8Text import Int8TextRecord
import struct
from typing import Union

"""Module pour la gestion des enregistrements de texte entier 64 bits"""

class Int64TextRecord(Int8TextRecord):
    type = 0x8E

    def to_bytes(self):
        return struct.pack('<B', self.type) + struct.pack('<q',
                self.value)

    @classmethod
    def parse(cls, fp):
        return cls(struct.unpack('<q', fp.read(8))[0])