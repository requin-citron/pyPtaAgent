from ..records.Int8Text import Int8TextRecord
import struct

"""Module pour la gestion des enregistrements de texte entier 32 bits"""

class Int32TextRecord(Int8TextRecord):
    """Classe pour la gestion des enregistrements de texte entier 32 bits
    
    Cette classe étend Int8TextRecord pour gérer les valeurs entières 32 bits.
    """
    type: int = 0x8C

    def __init__(self, value: int) -> None:
        """Initialise un enregistrement de texte entier 32 bits
        
        Args:
            value (int): Valeur entière 32 bits à stocker
        """
        super().__init__(value)

    def to_bytes(self) -> bytes:
        """Convertit l'enregistrement en bytes
        
        Returns:
            bytes: Représentation en bytes de l'enregistrement
        """
        return struct.pack('<B', self.type) + struct.pack('<i', self.value)

    @classmethod
    def parse(cls, fp) -> 'Int32TextRecord':
        """Parse un flux de bytes en un enregistrement de texte entier 32 bits
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            Int32TextRecord: Instance d'Int32TextRecord créée à partir du flux
        """
        value = struct.unpack('<i', fp.read(4))[0]
        return cls(value)