from ..base import Text
import struct
from typing import Union

"""Module pour la gestion des enregistrements de texte flottant"""

class FloatTextRecord(Text):
    """Classe pour la gestion des enregistrements de texte flottant
    
    Cette classe étend Text pour gérer les valeurs flottantes (32 bits).
    """
    type: int = 0x90

    def __init__(self, value: Union[float, int]) -> None:
        """Initialise un enregistrement de texte flottant
        
        Args:
            value (Union[float, int]): Valeur numérique à stocker
        """
        self.value: float = float(value)

    def to_bytes(self) -> bytes:
        """Convertit l'enregistrement en bytes
        
        Returns:
            bytes: Représentation en bytes de l'enregistrement
        """
        bytes = super(FloatTextRecord, self).to_bytes()
        bytes += struct.pack('<f', self.value)
        return bytes

    def __str__(self) -> str:
        """Convertit l'enregistrement en chaîne de caractères
        
        Returns:
            str: Représentation textuelle de la valeur
        
        Examples:
            >>> str(FloatTextRecord(float('-inf')))
            '-INF'
            >>> str(FloatTextRecord(-0.0))
            '-0'
            >>> str(FloatTextRecord(1.337))
            '1.337'
            >>> str(FloatTextRecord(1234567890))
            '1234567890'
            >>> str(FloatTextRecord(float('nan')))
            'NaN'
        """
        try:
            if self.value == int(self.value):
                return '%.0f' % self.value
            elif self.value == 0.0:
                return '0'
            else:
                return str(self.value)
        except:
            return str(self.value).upper()

    @classmethod
    def parse(cls, fp) -> 'FloatTextRecord':
        """Parse un flux de bytes en un enregistrement de texte flottant
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            FloatTextRecord: Instance de FloatTextRecord créée à partir du flux
        """
        value = struct.unpack('<f', fp.read(4))[0]
        return cls(value)
