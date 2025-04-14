from ..records.Int8Text import Int8TextRecord
import struct
from typing import Union

"""Module pour la gestion des enregistrements de texte entier 16 bits"""

class Int16TextRecord(Int8TextRecord):
    type = 0x8A

    def to_bytes(self):
        return struct.pack('<B', self.type) + struct.pack('<h',
                self.value)

    @classmethod
    def parse(cls, fp):
        return cls(struct.unpack('<h', fp.read(2))[0])