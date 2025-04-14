from ..base import Attribute, Record
from ..utils.types import Utf8String, MultiByteInt31
from ..utils.dictionary import dictionary
import struct

"""Module pour la gestion des attributs de dictionnaire XML"""

class DictionaryAttributeRecord(Attribute):
    """Classe pour la gestion des attributs de dictionnaire XML
    
    Cette classe étend Attribute pour gérer les attributs XML référencés dans un dictionnaire.
    """
    type: int = 0x07

    def __init__(self, prefix: str, index: int, value: Record) -> None:
        """Initialise un attribut de dictionnaire
        
        Args:
            prefix (str): Préfixe du namespace
            index (int): Index de la chaîne dans le dictionnaire
            value (Record): Valeur de l'attribut
        """
        self.prefix: str = prefix
        self.index: int = index
        self.value: Record = value

    def to_bytes(self) -> bytes:
        """Convertit l'attribut en bytes
        
        Returns:
            bytes: Représentation en bytes de l'attribut
        
        Example:
            >>> DictionaryAttributeRecord('x', 2, TrueTextRecord()).to_bytes()
            '\x07\x01x\x02\x86'
        """
        bytes = super(DictionaryAttributeRecord, self).to_bytes()
        bytes += Utf8String(self.prefix).to_bytes()
        bytes += MultiByteInt31(self.index).to_bytes()
        bytes += self.value.to_bytes()
        return bytes

    def __str__(self) -> str:
        """Convertit l'attribut en chaîne XML
        
        Returns:
            str: Représentation XML de l'attribut
        """
        return '%s:%s="%s"' % (self.prefix, dictionary[self.index], 
                str(self.value))
   
    @classmethod
    def parse(cls, fp) -> 'DictionaryAttributeRecord':
        """Parse un flux de bytes en un attribut de dictionnaire
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            DictionaryAttributeRecord: Instance de DictionaryAttributeRecord créée à partir du flux
        """
        prefix = Utf8String.parse(fp).value
        index = MultiByteInt31.parse(fp).value
        type = struct.unpack('<B', fp.read(1))[0]
        value = Record.records[type].parse(fp)
        return cls(prefix, index, value)