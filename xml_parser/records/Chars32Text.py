from ..records.Chars8Text import Chars8TextRecord
import struct

"""Module pour la gestion des enregistrements de texte (jusqu'à 32 caractères)"""

class Chars32TextRecord(Chars8TextRecord):
    """Classe pour la gestion des enregistrements de texte (jusqu'à 32 caractères)
    
    Cette classe étend Chars8TextRecord pour gérer les chaînes de caractères de taille limitée à 32 caractères.
    """
    type: int = 0x9C

    def to_bytes(self) -> bytes:
        """Convertit l'enregistrement en bytes
        
        Returns:
            bytes: Représentation en bytes de l'enregistrement
        """
        data: bytes = self.value.encode('utf-8')
        bytes: bytes = struct.pack('<B', self.type)
        bytes += struct.pack('<I', len(data))
        bytes += data
        return bytes

    @classmethod
    def parse(cls, fp) -> 'Chars32TextRecord':
        """Parse un flux de bytes en un enregistrement de texte
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            Chars32TextRecord: Instance de Chars32TextRecord créée à partir du flux
        """
        ln: int = struct.unpack('<I', fp.read(4))[0]
        value: str = fp.read(ln).decode('utf-8')
        return cls(value)