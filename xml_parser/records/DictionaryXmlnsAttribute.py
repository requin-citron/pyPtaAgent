from ..base import Attribute
from ..utils.types import Utf8String, MultiByteInt31
from ..utils.dictionary import dictionary
import struct

"""Module pour la gestion des attributs de namespace XML de dictionnaire"""

class DictionaryXmlnsAttributeRecord(Attribute):
    """Classe pour la gestion des attributs de namespace XML de dictionnaire
    
    Cette classe étend Attribute pour gérer les attributs xmlns XML référencés dans un dictionnaire.
    """
    type: int = 0x0B

    def __init__(self, prefix: str, index: int) -> None:
        """Initialise un attribut de namespace XML de dictionnaire
        
        Args:
            prefix (str): Préfixe du namespace
            index (int): Index de la chaîne dans le dictionnaire
        """
        self.prefix: str = prefix
        self.index: int = index

    def __str__(self) -> str:
        """Convertit l'attribut en chaîne XML
        
        Returns:
            str: Représentation XML de l'attribut
        """
        return 'xmlns:%s="%s"' % (self.prefix, dictionary[self.index])

    def to_bytes(self) -> bytes:
        """Convertit l'attribut en bytes
        
        Returns:
            bytes: Représentation en bytes de l'attribut
        
        Example:
            >>> DictionaryXmlnsAttributeRecord('a', 6).to_bytes()
            '\x0b\x01\x61\x06'
        """
        bytes = struct.pack('<B', self.type)
        bytes += Utf8String(self.prefix).to_bytes()
        bytes += MultiByteInt31(self.index).to_bytes()
        return bytes

    @classmethod
    def parse(cls, fp) -> 'DictionaryXmlnsAttributeRecord':
        """Parse un flux de bytes en un attribut de namespace XML de dictionnaire
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            DictionaryXmlnsAttributeRecord: Instance de DictionaryXmlnsAttributeRecord créée à partir du flux
        """
        prefix = Utf8String.parse(fp).value
        index = MultiByteInt31.parse(fp).value
        return cls(prefix, index)