from ..base import Text
from ..utils.dictionary import dictionary
from ..utils.types import MultiByteInt31

"""Module pour la gestion des enregistrements de texte de dictionnaire"""

class DictionaryTextRecord(Text):
    """Classe pour la gestion des enregistrements de texte de dictionnaire
    
    Cette classe étend Text pour gérer les références à des chaînes de caractères stockées dans un dictionnaire.
    """
    type: int = 0xAA

    def __init__(self, index: int) -> None:
        """Initialise un enregistrement de texte de dictionnaire
        
        Args:
            index (int): Index de la chaîne dans le dictionnaire
        """
        self.index: int = index

    def to_bytes(self) -> bytes:
        """Convertit l'enregistrement en bytes
        
        Returns:
            bytes: Représentation en bytes de l'enregistrement
        """
        return (super(DictionaryTextRecord, self).to_bytes() +
                MultiByteInt31(self.index).to_bytes())

    def __str__(self) -> str:
        """Convertit l'enregistrement en chaîne de caractères
        
        Returns:
            str: Chaîne de caractères correspondant à l'index dans le dictionnaire
        """
        return dictionary[self.index]

    @classmethod
    def parse(cls, fp) -> 'DictionaryTextRecord':
        """Parse un flux de bytes en un enregistrement de texte de dictionnaire
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            DictionaryTextRecord: Instance de DictionaryTextRecord créée à partir du flux
        """
        index = MultiByteInt31.parse(fp).value
        return cls(index)