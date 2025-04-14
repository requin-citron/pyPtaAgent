from ..records.Chars8Text import Chars8TextRecord
import struct

"""Module pour la gestion des enregistrements de texte (jusqu'à 16 caractères)"""

class Chars16TextRecord(Chars8TextRecord):
    """Classe pour la gestion des enregistrements de texte (jusqu'à 16 caractères)
    
    Cette classe étend Chars8TextRecord pour gérer les chaînes de caractères de taille limitée à 16 caractères.
    """
    type: int = 0x9A

    def to_bytes(self) -> bytes:
        """Convertit l'enregistrement en bytes
        
        Returns:
            bytes: Représentation en bytes de l'enregistrement
        """
        data: bytes = self.value.encode('utf-8')
        bytes: bytes = struct.pack('<B', self.type)
        bytes += struct.pack('<H', len(data))
        bytes += data
        return bytes

    @classmethod
    def parse(cls, fp) -> 'Chars16TextRecord':
        """Parse un flux de bytes en un enregistrement de texte
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            Chars16TextRecord: Instance de Chars16TextRecord créée à partir du flux
        """
        ln: int = struct.unpack('<H', fp.read(2))[0]
        value: str = fp.read(ln).decode('utf-8')
        return cls(value)