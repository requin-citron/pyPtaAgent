from ..records.Int64Text import Int64TextRecord
import struct
from typing import Union

"""Module pour la gestion des enregistrements de texte entier non signé 64 bits"""

class UInt64TextRecord(Int64TextRecord):
    """Classe pour la gestion des enregistrements de texte entier non signé 64 bits
    
    Cette classe étend Int64TextRecord pour gérer les valeurs entières non signées 64 bits,
    avec une plage de valeurs de 0 à 18446744073709551615.
    """
    type: int = 0xB2

    def __init__(self, value: Union[int, str]) -> None:
        """Initialise un enregistrement de texte entier non signé 64 bits
        
        Args:
            value (Union[int, str]): Valeur entière non signée 64 bits à stocker
        
        Raises:
            ValueError: Si la valeur est en dehors de la plage [0, 18446744073709551615]
        """
        if isinstance(value, str):
            value = int(value)
        if not (0 <= value <= 18446744073709551615):
            raise ValueError(f"Valeur hors plage pour uint64: {value}")
        self.value: int = value

    def to_bytes(self) -> bytes:
        """Convertit l'enregistrement en bytes
        
        Returns:
            bytes: Représentation en bytes de l'enregistrement
        """
        return struct.pack('<B', self.type) + struct.pack('<Q', self.value)

    def __str__(self) -> str:
        """Convertit l'enregistrement en chaîne de caractères
        
        Returns:
            str: Représentation textuelle de la valeur
        """
        return str(self.value)

    @classmethod
    def parse(cls, fp) -> 'UInt64TextRecord':
        """Parse un flux de bytes en un enregistrement de texte entier non signé 64 bits
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            UInt64TextRecord: Instance de UInt64TextRecord créée à partir du flux
            
        Raises:
            struct.error: Si la lecture des bytes échoue
        """
        return cls(struct.unpack('<Q', fp.read(8))[0])