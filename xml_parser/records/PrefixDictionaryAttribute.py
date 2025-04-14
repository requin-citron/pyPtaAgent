from ..records.DictionaryAttribute import DictionaryAttributeRecord
from ..base import Record
from ..utils.types import MultiByteInt31
import struct

"""Module pour la gestion des attributs de dictionnaire avec préfixe XML"""

class PrefixDictionaryAttributeRecord(DictionaryAttributeRecord):
    """Classe pour la gestion des attributs de dictionnaire avec préfixe XML
    
    Cette classe étend DictionaryAttributeRecord pour gérer les attributs XML avec préfixe de namespace,
    où le nom de l'attribut est référencé dans un dictionnaire.
    """
    type: int = 0x09

    def __init__(self, index: int, value: Record) -> None:
        """Initialise un attribut de dictionnaire avec préfixe
        
        Args:
            index (int): Index du nom de l'attribut dans le dictionnaire
            value (Record): Valeur de l'attribut
        """
        self.index: int = index
        self.value: Record = value
        super(PrefixDictionaryAttributeRecord, self).__init__(self.char, index, value)

    def to_bytes(self) -> bytes:
        """Convertit l'attribut en bytes
        
        Returns:
            bytes: Représentation en bytes de l'attribut
        """
        idx = MultiByteInt31(self.index)
        return (struct.pack('<B', self.type) + idx.to_bytes() +
                self.value.to_bytes())

    @classmethod
    def parse(cls, fp) -> 'PrefixDictionaryAttributeRecord':
        """Parse un flux de bytes en un attribut de dictionnaire avec préfixe
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            PrefixDictionaryAttributeRecord: Instance de PrefixDictionaryAttributeRecord créée à partir du flux
        """
        index = MultiByteInt31.parse(fp).value
        type = struct.unpack('<B', fp.read(1))[0]
        value = Record.records[type].parse(fp)
        return cls(index, value)