from ..base import Attribute, Record
from ..utils.types import MultiByteInt31
from ..utils.dictionary import dictionary
import struct
from typing import Any

"""Module pour la gestion des attributs de dictionnaire XML courts"""

class ShortDictionaryAttributeRecord(Attribute):
    """Classe pour la gestion des attributs de dictionnaire XML courts
    
    Cette classe étend Attribute pour gérer les attributs XML référencés dans un dictionnaire,
    avec une représentation optimisée pour les petits index.
    """
    type: int = 0x06

    def __init__(self, index: int, value: Record) -> None:
        """Initialise un attribut de dictionnaire court
        
        Args:
            index (int): Index de la chaîne dans le dictionnaire
            value (Record): Valeur de l'attribut
        """
        self.index: int = index
        self.value: Record = value

    def to_bytes(self) -> bytes:
        """Convertit l'attribut en bytes
        
        Returns:
            bytes: Représentation en bytes de l'attribut
        
        Example:
            >>> ShortDictionaryAttributeRecord(3, TrueTextRecord()).to_bytes()
            '\x06\x03\x86'
        """
        bytes = super(ShortDictionaryAttributeRecord, self).to_bytes()
        bytes += MultiByteInt31(self.index).to_bytes()
        bytes += self.value.to_bytes()
        return bytes

    def __str__(self) -> str:
        """Convertit l'attribut en chaîne XML
        
        Returns:
            str: Représentation XML de l'attribut
        """
        return '%s="%s"' % (dictionary[self.index], str(self.value))

    @classmethod
    def parse(cls, fp) -> 'ShortDictionaryAttributeRecord':
        """Parse un flux de bytes en un attribut de dictionnaire court
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            ShortDictionaryAttributeRecord: Instance de ShortDictionaryAttributeRecord créée à partir du flux
        """
        index = MultiByteInt31.parse(fp).value
        type = struct.unpack('<B', fp.read(1))[0]
        value = Record.records[type].parse(fp)
        return cls(index, value)