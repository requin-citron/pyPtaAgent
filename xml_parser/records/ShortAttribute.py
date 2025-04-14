from ..base import Attribute, Record
from ..utils.types import Utf8String
import struct
from typing import Any

"""Module pour la gestion des attributs XML courts"""

class ShortAttributeRecord(Attribute):
    """Classe pour la gestion des attributs XML courts
    
    Cette classe étend Attribute pour gérer les attributs XML simples avec un nom court.
    """
    type: int = 0x04

    def __init__(self, name: str, value: Record) -> None:
        """Initialise un attribut XML court
        
        Args:
            name (str): Nom de l'attribut
            value (Record): Valeur de l'attribut
        """
        self.name: str = name
        self.value: Record = value

    def to_bytes(self) -> bytes:
        """Convertit l'attribut en bytes
        
        Returns:
            bytes: Représentation en bytes de l'attribut
        
        Example:
            >>> ShortAttributeRecord('test', TrueTextRecord()).to_bytes()
            '\x04\x04test\x86'
        """
        bytes = super(ShortAttributeRecord, self).to_bytes()
        bytes += Utf8String(self.name).to_bytes()
        bytes += self.value.to_bytes()
        return bytes

    def __str__(self) -> str:
        """Convertit l'attribut en chaîne XML
        
        Returns:
            str: Représentation XML de l'attribut
        """
        return '%s="%s"' % (self.name, str(self.value))

    @classmethod
    def parse(cls, fp) -> 'ShortAttributeRecord':
        """Parse un flux de bytes en un attribut XML court
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            ShortAttributeRecord: Instance de ShortAttributeRecord créée à partir du flux
        """
        name = Utf8String.parse(fp).value
        type = struct.unpack('<B', fp.read(1))[0]
        value = Record.records[type].parse(fp)
        return cls(name, value)