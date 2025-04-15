from ..base import Attribute
from ..utils.types import MultiByteInt31
from ..utils.dictionary import dictionary
import struct
from typing import Any

"""Module pour la gestion des attributs XMLNS de dictionnaire courts"""

class ShortDictionaryXmlnsAttributeRecord(Attribute):
    """Classe pour la gestion des attributs XMLNS de dictionnaire courts
    
    Cette classe étend Attribute pour gérer les attributs XMLNS référencés dans un dictionnaire,
    avec une représentation optimisée pour les petits index.
    """
    type: int = 0x0a

    def __init__(self, index: int, *args, **kwargs) -> None:
        """Initialise un attribut XMLNS de dictionnaire court
        
        Args:
            index (int): Index de la chaîne dans le dictionnaire
            *args: Arguments supplémentaires
            **kwargs: Arguments supplémentaires nommés
        """
        self.index: int = index
        self.value: str = dictionary[self.index]
        super(ShortDictionaryXmlnsAttributeRecord, self).__init__(*args, **kwargs)

    def to_bytes(self) -> bytes:
        """Convertit l'attribut en bytes
        
        Returns:
            bytes: Représentation en bytes de l'attribut
        """
        bytes = struct.pack('<B', self.type)
        bytes += MultiByteInt31(self.index).to_bytes()
        return bytes

    def __str__(self) -> str:
        """Convertit l'attribut en chaîne XML
        
        Returns:
            str: Représentation XML de l'attribut
        """
        return 'xmlns="%s"' % (self.value,)

    @classmethod
    def parse(cls, fp) -> 'ShortDictionaryXmlnsAttributeRecord':
        """Parse un flux de bytes en un attribut XMLNS de dictionnaire court
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            ShortDictionaryXmlnsAttributeRecord: Instance de ShortDictionaryXmlnsAttributeRecord créée à partir du flux
        """
        index = MultiByteInt31.parse(fp).value
        return cls(index)