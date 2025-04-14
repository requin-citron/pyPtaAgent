from ..base import Attribute
from ..utils.types import Utf8String
from typing import Any
import struct

"""Module pour la gestion des attributs XMLNS"""

class XmlnsAttributeRecord(Attribute):
    """Classe pour la gestion des attributs XMLNS
    
    Cette classe étend Attribute pour gérer les attributs XMLNS avec un nom et une valeur,
    utilisant l'encodage UTF-8 pour les chaînes de caractères.
    """
    type: int = 0x09

    def __init__(self, name: str, value: str, *args, **kwargs) -> None:
        """Initialise un attribut XMLNS
        
        Args:
            name (str): Nom de l'attribut XMLNS
            value (str): Valeur de l'attribut XMLNS
            *args: Arguments supplémentaires
            **kwargs: Arguments supplémentaires nommés
        """
        super(XmlnsAttributeRecord, self).__init__(*args, **kwargs)
        self.name: str = name
        self.value: str = value

    def to_bytes(self) -> bytes:
        """Convertit l'attribut en bytes
        
        Returns:
            bytes: Représentation en bytes de l'attribut
        """
        bytes = struct.pack('<B', self.type)
        bytes += Utf8String(self.name).to_bytes()
        bytes += Utf8String(self.value).to_bytes()
        return bytes

    def __str__(self) -> str:
        """Convertit l'attribut en chaîne XML
        
        Returns:
            str: Représentation XML de l'attribut
        """
        return 'xmlns:%s="%s"' % (self.name, self.value)

    @classmethod
    def parse(cls, fp) -> 'XmlnsAttributeRecord':
        """Parse un flux de bytes en un attribut XMLNS
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            XmlnsAttributeRecord: Instance de XmlnsAttributeRecord créée à partir du flux
        """
        name = Utf8String.parse(fp).value
        value = Utf8String.parse(fp).value
        return cls(name, value)