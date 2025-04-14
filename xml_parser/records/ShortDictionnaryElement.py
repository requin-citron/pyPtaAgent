from ..base import Element
from ..utils.dictionary import dictionary
from ..utils.types import MultiByteInt31
from typing import List

"""Module pour la gestion des éléments de dictionnaire XML courts"""

class ShortDictionaryElementRecord(Element):
    """Classe pour la gestion des éléments de dictionnaire XML courts
    
    Cette classe étend Element pour gérer les éléments XML référencés dans un dictionnaire,
    avec une représentation optimisée pour les petits index.
    """
    type: int = 0x42

    def __init__(self, index: int, *args, **kwargs) -> None:
        """Initialise un élément de dictionnaire court
        
        Args:
            index (int): Index du nom de l'élément dans le dictionnaire
            *args: Arguments supplémentaires
            **kwargs: Arguments supplémentaires nommés
        """
        self.childs: List[Element] = []
        self.index: int = index
        self.attributes: List[Element] = []  # Changed from Attribute to Element
        self.name: str = dictionary[self.index]
        super(ShortDictionaryElementRecord, self).__init__(*args, **kwargs)

    def __str__(self) -> str:
        """Convertit l'élément en chaîne XML
        
        Returns:
            str: Représentation XML de l'élément avec ses attributs
        """
        return '<%s %s>' % (self.name, ' '.join([str(a) for a in self.attributes]))

    def to_bytes(self) -> bytes:
        """Convertit l'élément en bytes
        
        Returns:
            bytes: Représentation en bytes de l'élément
        
        Example:
            >>> ShortDictionaryElementRecord(2).to_bytes()
            'B\x02'
        """
        string = MultiByteInt31(self.index)
        bytes = (super(ShortDictionaryElementRecord, self).to_bytes() +
                string.to_bytes())

        for attr in self.attributes:
            bytes += attr.to_bytes()
        return bytes

    @classmethod
    def parse(cls, fp) -> 'ShortDictionaryElementRecord':
        """Parse un flux de bytes en un élément de dictionnaire court
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            ShortDictionaryElementRecord: Instance de ShortDictionaryElementRecord créée à partir du flux
        """
        index = MultiByteInt31.parse(fp).value
        return cls(index)