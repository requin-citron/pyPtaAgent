from ..base import Text
import struct
from decimal import Decimal

"""Module pour la gestion des enregistrements de texte décimal"""

class DecimalTextRecord(Text):
    """Classe pour la gestion des enregistrements de texte décimal
    
    Cette classe étend Text pour gérer les valeurs décimales précises.
    """
    type: int = 0x94

    def __init__(self, value: Decimal) -> None:
        """Initialise un enregistrement de texte décimal
        
        Args:
            value (Decimal): Valeur décimale à stocker
        """
        self.value: Decimal = value

    def __str__(self) -> str:
        """Convertit l'enregistrement en chaîne de caractères
        
        Returns:
            str: Représentation textuelle de la valeur décimale
        """
        return str(self.value)

    def to_bytes(self) -> bytes:
        """Convertit l'enregistrement en bytes
        
        Returns:
            bytes: Représentation en bytes de l'enregistrement
        """
        return (super(DecimalTextRecord, self).to_bytes() +
                self.value.to_bytes())

    @classmethod
    def parse(cls, fp) -> 'DecimalTextRecord':
        """Parse un flux de bytes en un enregistrement de texte décimal
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            DecimalTextRecord: Instance de DecimalTextRecord créée à partir du flux
        """
        value = Decimal.parse(fp)
        return cls(value)