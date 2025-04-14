from ..records.FloatText import FloatTextRecord
import struct
from typing import Union

"""Module pour la gestion des enregistrements de texte double précision"""

class DoubleTextRecord(FloatTextRecord):
    """Classe pour la gestion des enregistrements de texte double précision
    
    Cette classe étend FloatTextRecord pour gérer les nombres à double précision (64 bits).
    """
    type: int = 0x92

    def __init__(self, value: Union[float, int]) -> None:
        """Initialise un enregistrement de texte double précision
        
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
        bytes += struct.pack('<d', self.value)
        return bytes

    def __str__(self) -> str:
        """Convertit l'enregistrement en chaîne de caractères
        
        Returns:
            str: Représentation textuelle de la valeur
        
        Examples:
            >>> str(DoubleTextRecord(float('-inf')))
            '-INF'
            >>> str(DoubleTextRecord(-0.0))
            '-0'
            >>> str(DoubleTextRecord(1.337))
            '1.337'
            >>> str(DoubleTextRecord(1234567890123456789.0))
            '1234567890123456789.0'
            >>> str(DoubleTextRecord(0.0))
            '0'
            >>> str(DoubleTextRecord(float('nan')))
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
    def parse(cls, fp) -> 'DoubleTextRecord':
        """Parse un flux de bytes en un enregistrement de texte double précision
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            DoubleTextRecord: Instance de DoubleTextRecord créée à partir du flux
        """
        value = struct.unpack('<d', fp.read(8))[0]
        return cls(value)