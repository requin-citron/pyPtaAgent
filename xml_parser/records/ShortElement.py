from ..base import Element
from ..utils.types import Utf8String
from typing import List

"""Module pour la gestion des éléments XML courts"""

class ShortElementRecord(Element):
    """Classe pour la gestion des éléments XML courts
    
    Cette classe étend Element pour gérer les éléments XML simples avec un nom court.
    """
    type: int = 0x40

    def __init__(self, name: str, *args, **kwargs) -> None:
        """Initialise un élément XML court
        
        Args:
            name (str): Nom de l'élément
            *args: Arguments supplémentaires
            **kwargs: Arguments supplémentaires nommés
        """
        self.childs: List[Element] = []
        self.name: str = name
        self.attributes: List[Element] = []  # Modified here
        super(ShortElementRecord, self).__init__(*args, **kwargs)

    def to_bytes(self) -> bytes:
        """Convertit l'élément en bytes
        
        Returns:
            bytes: Représentation en bytes de l'élément
        
        Example:
            >>> ShortElementRecord('Envelope').to_bytes()
            '@\x08Envelope'
        """
        string = Utf8String(self.name)
        bytes = (super(ShortElementRecord, self).to_bytes() +
                string.to_bytes())

        for attr in self.attributes:
            bytes += attr.to_bytes()
        return bytes

    def __str__(self) -> str:
        """Convertit l'élément en chaîne XML
        
        Returns:
            str: Représentation XML de l'élément avec ses attributs
        """
        return '<%s %s>' % (self.name, 
                ' '.join([str(a) for a in self.attributes]))

    @classmethod
    def parse(cls, fp) -> 'ShortElementRecord':
        """Parse un flux de bytes en un élément XML court
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            ShortElementRecord: Instance de ShortElementRecord créée à partir du flux
        """
        name = Utf8String.parse(fp).value
        return cls(name)