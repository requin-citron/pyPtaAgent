from ..records.UnicodeChars8Text import UnicodeChars8TextRecord
import struct
from typing import Union, Type

"""Module pour la gestion des enregistrements de texte Unicode 16 bits avec longueur"""

class UnicodeChars16TextRecord(UnicodeChars8TextRecord):
    """Classe pour la gestion des enregistrements de texte Unicode 16 bits avec longueur
    
    Cette classe étend UnicodeChars8TextRecord pour gérer les chaînes de caractères Unicode encodées sur 16 bits,
    avec une longueur préfixe de 2 octets pour la gestion des chaînes de caractères.
    """
    type: int = 0xB8

    def __init__(self, value: Union[str, bytes]) -> None:
        """Initialise un enregistrement de texte Unicode 16 bits avec longueur
        
        Args:
            value (Union[str, bytes]): Chaîne de caractères ou bytes à stocker
        """
        if isinstance(value, str):
            self.value: str = value
        else:
            self.value = value.decode('utf-16-le')

    def to_bytes(self) -> bytes:
        """Convertit l'enregistrement en bytes
        
        Returns:
            bytes: Représentation en bytes de l'enregistrement
        
        Example:
            >>> UnicodeChars16TextRecord('abc').to_bytes()
            '\xb8\x00\x06a\x00b\x00c\x00'
        """
        data = self.value.encode('utf-16-le')[2:]  # Skip BOM
        bytes = struct.pack('<B', self.type)
        bytes += struct.pack('<H', len(data))
        bytes += data
        return bytes

    def __str__(self) -> str:
        """Convertit l'enregistrement en chaîne de caractères
        
        Returns:
            str: Représentation textuelle de la valeur
        """
        return self.value

    @classmethod
    def parse(cls, fp) -> 'UnicodeChars16TextRecord':
        """Parse un flux de bytes en un enregistrement de texte Unicode 16 bits avec longueur
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            UnicodeChars16TextRecord: Instance de UnicodeChars16TextRecord créée à partir du flux
        
        Example:
            >>> import io
            >>> fp = io.BytesIO(b'\x00\x06a\x00b\x00c\x00')
            >>> str(UnicodeChars16TextRecord.parse(fp))
            'abc'
        """
        length = struct.unpack('<H', fp.read(2))[0]
        data = fp.read(length)
        return cls(data.decode('utf-16-le'))