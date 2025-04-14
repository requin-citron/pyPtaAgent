from ..base import Text
import struct
from typing import Union

"""Module pour la gestion des enregistrements de texte entier 8 bits"""

class Int8TextRecord(Text):
    type = 0x88

    def __init__(self, value):
        self.value = value

    def to_bytes(self):
        return super(Int8TextRecord, self).to_bytes() + struct.pack('<b',
                self.value)

    def __str__(self):
        return str(self.value)

    @classmethod
    def parse(cls, fp):
        return cls(struct.unpack('<b', fp.read(1))[0])