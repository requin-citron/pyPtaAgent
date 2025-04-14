from ..base import Text
import struct
from ..utils.dictionary import dictionary
from typing import Tuple

"""Module pour la gestion des enregistrements de texte QName de dictionnaire"""

class QNameDictionaryTextRecord(Text):
    """Classe pour la gestion des enregistrements de texte QName de dictionnaire
    
    Cette classe étend Text pour gérer les références à des chaînes de caractères avec préfixe,
    où le nom est référencé dans un dictionnaire.
    """
    type: int = 0xBC

    def __init__(self, prefix: str, index: int) -> None:
        """Initialise un enregistrement de texte QName de dictionnaire
        
        Args:
            prefix (str): Préfixe du namespace
            index (int): Index du nom dans le dictionnaire
        """
        self.prefix: str = prefix
        self.index: int = index

    def to_bytes(self) -> bytes:
        """Convertit l'enregistrement en bytes
        
        Returns:
            bytes: Représentation en bytes de l'enregistrement
        
        Example:
            >>> QNameDictionaryTextRecord('b', 2).to_bytes()
            '\xbc\x01\x00\x00\x02'
        """
        bytes = struct.pack('<B', self.type)
        bytes += struct.pack('<B', ord(self.prefix) - ord('a'))
        bytes += struct.pack('<BBB',
                        (self.index >> 16) & 0xFF,
                        (self.index >>  8) & 0xFF,
                        (self.index >>  0) & 0xFF)
        return bytes
 
    def __str__(self) -> str:
        """Convertit l'enregistrement en chaîne de caractères
        
        Returns:
            str: Représentation textuelle du QName
        
        Example:
            >>> str(QNameDictionaryTextRecord('b', 2))
            'b:Envelope'
        """
        return '%s:%s' % (self.prefix, dictionary[self.index])

    @classmethod
    def parse(cls, fp) -> 'QNameDictionaryTextRecord':
        """Parse un flux de bytes en un enregistrement de texte QName de dictionnaire
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            QNameDictionaryTextRecord: Instance de QNameDictionaryTextRecord créée à partir du flux
        
        Example:
            >>> import StringIO
            >>> fp = StringIO.StringIO('\x01\x00\x00\x02')
            >>> str(QNameDictionaryTextRecord.parse(fp))
            'b:Envelope'
        """
        prefix = chr(struct.unpack('<B', fp.read(1))[0] + ord('a'))
        idx = struct.unpack('<BBB', fp.read(3))
        index = idx[0] << 16 | idx[1] << 8 | idx[2]
        return cls(prefix, index)
