from ..records.DictionaryElement import DictionaryElementRecord
from ..utils.types import MultiByteInt31
import struct
from typing import List

"""Module pour la gestion des éléments de dictionnaire avec préfixe XML"""

class PrefixDictionaryElementRecord(DictionaryElementRecord):
    """Classe pour la gestion des éléments de dictionnaire avec préfixe XML
    
    Cette classe étend DictionaryElementRecord pour gérer les éléments XML avec préfixe de namespace,
    où le nom de l'élément est référencé dans un dictionnaire.
    """
    type: int = 0x44

    def __init__(self, index: int) -> None:
        """Initialise un élément de dictionnaire avec préfixe
        
        Args:
            index (int): Index du nom de l'élément dans le dictionnaire
        """
        self.index: int = index
        self.attributes: List[Attribute] = []
        super(PrefixDictionaryElementRecord, self).__init__(self.char, index)

    def to_bytes(self) -> bytes:
        """Convertit l'élément en bytes
        
        Returns:
            bytes: Représentation en bytes de l'élément
        """
        string = MultiByteInt31(self.index)
        bytes = (struct.pack('<B', self.type) +
                string.to_bytes())

        for attr in self.attributes:
            bytes += attr.to_bytes()
        return bytes

    @classmethod
    def parse(cls, fp) -> 'PrefixDictionaryElementRecord':
        """Parse un flux de bytes en un élément de dictionnaire avec préfixe
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            PrefixDictionaryElementRecord: Instance de PrefixDictionaryElementRecord créée à partir du flux
        """
        index = MultiByteInt31.parse(fp).value
        return cls(index)