from ..base import Text
import struct

"""Module pour la gestion des enregistrements de texte booléen"""

class BoolTextRecord(Text):
    """Classe pour la gestion des enregistrements de texte booléen
    
    Cette classe étend Text pour gérer les valeurs booléennes dans les enregistrements XML.
    """
    type: int = 0xB4

    def __init__(self, value: bool) -> None:
        """Initialise un enregistrement de texte booléen
        
        Args:
            value (bool): Valeur booléenne à stocker
        """
        self.value: bool = value

    def to_bytes(self) -> bytes:
        """Convertit l'enregistrement en bytes
        
        Returns:
            bytes: Représentation en bytes de l'enregistrement
        """
        return (struct.pack('<B', self.type) +
                struct.pack('<B', 1 if self.value else 0))

    def __str__(self) -> str:
        """Convertit l'enregistrement en chaîne de caractères
        
        Returns:
            str: Représentation textuelle de la valeur booléenne
        """
        return str(self.value)

    @classmethod
    def parse(cls, fp) -> 'BoolTextRecord':
        """Parse un flux de bytes en un enregistrement de texte booléen
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            BoolTextRecord: Instance de BoolTextRecord créée à partir du flux
        """
        value = True if struct.unpack('<B', fp.read(1))[0] == 1 else False
        return cls(value)