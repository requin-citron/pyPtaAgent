from ..base import Text
import struct
from typing import Union, Type

"""Module pour la gestion des enregistrements de texte Unicode 8 bits avec longueur"""

class UnicodeChars8TextRecord(Text):
    """Classe pour la gestion des enregistrements de texte Unicode 8 bits avec longueur
    
    Cette classe étend Text pour gérer les chaînes de caractères Unicode encodées sur 8 bits,
    avec une longueur préfixe pour la gestion des chaînes de caractères.
    """
    type: int = 0xB6

    def __init__(self, value: Union[str, bytes]) -> None:
        """Initialise un enregistrement de texte Unicode 8 bits avec longueur
        
        Args:
            value (Union[str, bytes]): Chaîne de caractères ou bytes à stocker
        """
        if isinstance(value, str):
            self.value: str = value
        else:
            self.value = value.decode('utf-8')

    def to_bytes(self) -> bytes:
        """Convertit l'enregistrement en bytes
        
        Returns:
            bytes: Représentation en bytes de l'enregistrement
        
        Example:
            >>> UnicodeChars8TextRecord('abc').to_bytes()
            '\xb6\x06a\x00b\x00c\x00'
            >>> UnicodeChars8TextRecord('abc').to_bytes()
            '\xb6\x06a\x00b\x00c\x00'
        """
        data = self.value.encode('utf-8')
        bytes = struct.pack('<B', self.type)
        bytes += struct.pack('<B', len(data))
        bytes += data
        return bytes

    def __str__(self) -> str:
        """Convertit l'enregistrement en chaîne de caractères
        
        Returns:
            str: Représentation textuelle de la valeur
        """
        return self.value

    @classmethod
    def parse(cls, fp) -> 'UnicodeChars8TextRecord':
        """Parse un flux de bytes en un enregistrement de texte Unicode 8 bits avec longueur
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            UnicodeChars8TextRecord: Instance de UnicodeChars8TextRecord créée à partir du flux
        
        Example:
            >>> import io
            >>> fp = io.BytesIO(b'\x06a\x00b\x00c\x00')
            >>> str(UnicodeChars8TextRecord.parse(fp))
            'abc'
        """
        length = struct.unpack('<B', fp.read(1))[0]
        data = fp.read(length)
        return cls(data.decode('utf-8'))