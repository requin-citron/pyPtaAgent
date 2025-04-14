from ..base import Text
import struct
import datetime
from typing import Any

"""Module pour la gestion des enregistrements de texte TimeSpan"""

class TimeSpanTextRecord(Text):
    """Classe pour la gestion des enregistrements de texte TimeSpan
    
    Cette classe étend Text pour gérer les valeurs TimeSpan représentées en millisecondes.
    """
    type: int = 0xAE

    def __init__(self, value: int) -> None:
        """Initialise un enregistrement de texte TimeSpan
        
        Args:
            value (int): Nombre de millisecondes pour le TimeSpan
        """
        self.value: int = value

    def to_bytes(self) -> bytes:
        """Convertit l'enregistrement en bytes
        
        Returns:
            bytes: Représentation en bytes de l'enregistrement
        """
        return super(TimeSpanTextRecord, self).to_bytes() + struct.pack('<q', self.value)

    def __str__(self) -> str:
        """Convertit l'enregistrement en chaîne de caractères
        
        Returns:
            str: Représentation textuelle du TimeSpan en format ISO 8601
        """
        return str(datetime.timedelta(milliseconds=self.value/100))

    @classmethod
    def parse(cls, fp) -> 'TimeSpanTextRecord':
        """Parse un flux de bytes en un enregistrement de texte TimeSpan
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            TimeSpanTextRecord: Instance de TimeSpanTextRecord créée à partir du flux
        """
        value = struct.unpack('<q', fp.read(8))[0]
        return cls(value)