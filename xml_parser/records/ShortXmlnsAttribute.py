from ..base import Attribute
from ..utils.types import Utf8String
import struct
from typing import Any

"""Module pour la gestion des attributs XMLNS courts"""

class ShortXmlnsAttributeRecord(Attribute):
    """Classe pour la gestion des attributs XMLNS courts
    
    Cette classe étend Attribute pour gérer les attributs XMLNS simples avec une valeur courte.
    """
    type: int = 0x08

    def __init__(self, value: str, *args, **kwargs) -> None:
        """Initialise un attribut XMLNS court
        
        Args:
            value (str): Valeur de l'attribut XMLNS
            *args: Arguments supplémentaires
            **kwargs: Arguments supplémentaires nommés
        """
        self.value: str = value
        super(ShortXmlnsAttributeRecord, self).__init__(*args, **kwargs)

    def to_bytes(self) -> bytes:
        """Convertit l'attribut en bytes
        
        Returns:
            bytes: Représentation en bytes de l'attribut
        """
        bytes = struct.pack('<B', self.type)
        bytes += Utf8String(self.value).to_bytes()
        return bytes

    def __str__(self) -> str:
        """Convertit l'attribut en chaîne XML
        
        Returns:
            str: Représentation XML de l'attribut
        """
        return 'xmlns="%s"' % (self.value,)

    @classmethod
    def parse(cls, fp) -> 'ShortXmlnsAttributeRecord':
        """Parse un flux de bytes en un attribut XMLNS court
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            ShortXmlnsAttributeRecord: Instance de ShortXmlnsAttributeRecord créée à partir du flux
        """
        value = Utf8String.parse(fp).value
        return cls(value)