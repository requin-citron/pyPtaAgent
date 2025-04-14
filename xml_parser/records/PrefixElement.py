from ..records.Element import ElementRecord
from ..utils.types import Utf8String
import struct
from typing import List

"""Module pour la gestion des éléments avec préfixe XML"""

class PrefixElementRecord(ElementRecord):
    """Classe pour la gestion des éléments avec préfixe XML
    
    Cette classe étend ElementRecord pour gérer les éléments XML avec préfixe de namespace.
    """
    type: int = 0x41

    def __init__(self, name: str) -> None:
        """Initialise un élément avec préfixe
        
        Args:
            name (str): Nom de l'élément
        """
        self.name: str = name
        self.attributes: List[Attribute] = []
        super(PrefixElementRecord, self).__init__(self.char, name)

    def to_bytes(self) -> bytes:
        """Convertit l'élément en bytes
        
        Returns:
            bytes: Représentation en bytes de l'élément
        """
        string = Utf8String(self.name)
        bytes = (struct.pack('<B', self.type) +
                string.to_bytes())

        for attr in self.attributes:
            bytes += attr.to_bytes()
        return bytes

    @classmethod
    def parse(cls, fp) -> 'PrefixElementRecord':
        """Parse un flux de bytes en un élément avec préfixe
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            PrefixElementRecord: Instance de PrefixElementRecord créée à partir du flux
        """
        name = Utf8String.parse(fp).value
        return cls(name)