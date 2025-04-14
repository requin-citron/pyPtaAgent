from ..utils.types import Utf8String, MultiByteInt31
from ..utils.dictionary import dictionary
from ..base import Element
from typing import List

"""Module pour la gestion des éléments de dictionnaire XML"""

class DictionaryElementRecord(Element):
    """Classe pour la gestion des éléments de dictionnaire XML
    
    Cette classe étend Element pour gérer les éléments XML référencés dans un dictionnaire.
    """
    type: int = 0x43

    def __init__(self, prefix: str, index: int, *args, **kwargs) -> None:
        """Initialise un élément de dictionnaire
        
        Args:
            prefix (str): Préfixe du namespace
            index (int): Index de la chaîne dans le dictionnaire
            *args: Arguments additionnels
            **kwargs: Arguments nommés additionnels
        """
        self.childs: List[Element] = []
        self.prefix: str = prefix
        self.index: int = index
        self.attributes: List[Attribute] = []
        self.name: str = dictionary[self.index]

    def __str__(self) -> str:
        """Convertit l'élément en chaîne XML
        
        Returns:
            str: Représentation XML de l'élément
        
        Example:
            >>> str(DictionaryElementRecord('x', 2))
            '<x:Envelope >'
        """
        return '<%s:%s %s>' % (self.prefix, self.name, 
                ' '.join([str(a) for a in self.attributes]))
   
    def to_bytes(self) -> bytes:
        """Convertit l'élément en bytes
        
        Returns:
            bytes: Représentation en bytes de l'élément
        
        Example:
            >>> DictionaryElementRecord('x', 2).to_bytes()
            'C\x01x\x02'
        """
        pref = Utf8String(self.prefix)
        string = MultiByteInt31(self.index)

        bytes = (super(DictionaryElementRecord, self).to_bytes() +
                pref.to_bytes() +
                string.to_bytes())

        for attr in self.attributes:
            bytes += attr.to_bytes()
        return bytes

    @classmethod
    def parse(cls, fp) -> 'DictionaryElementRecord':
        """Parse un flux de bytes en un élément de dictionnaire
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            DictionaryElementRecord: Instance de DictionaryElementRecord créée à partir du flux
        """
        prefix = Utf8String.parse(fp).value
        index = MultiByteInt31.parse(fp).value
        return cls(prefix, index)
