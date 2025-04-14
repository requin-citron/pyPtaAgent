from ..records.Bytes8Text import Bytes8TextRecord
import struct, base64

"""Module pour la gestion des enregistrements de texte binaire (jusqu'à 32 bytes)"""

class Bytes32TextRecord(Bytes8TextRecord):
    """Classe pour la gestion des enregistrements de texte binaire (jusqu'à 32 bytes)
    
    Cette classe étend Bytes8TextRecord pour gérer les données binaires de taille limitée à 32 bytes.
    """
    type: int = 0xA2

    def __init__(self, data: bytes) -> None:
        """Initialise un enregistrement de texte binaire
        
        Args:
            data (bytes): Données binaires à stocker (max 32 bytes)
        """
        self.value: bytes = data

    def __str__(self) -> str:
        """Convertit l'enregistrement en chaîne de caractères encodée en base64
        
        Returns:
            str: Représentation en base64 des données binaires
        """
        return base64.b64encode(self.value).decode()

    def to_bytes(self) -> bytes:
        """Convertit l'enregistrement en bytes
        
        Returns:
            bytes: Représentation en bytes de l'enregistrement
        """
        bytes = struct.pack('<B', self.type)
        bytes += struct.pack('<I', len(self.value))
        bytes += self.value
        return bytes

    @classmethod
    def parse(cls, fp) -> 'Bytes32TextRecord':
        """Parse un flux de bytes en un enregistrement de texte binaire
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            Bytes32TextRecord: Instance de Bytes32TextRecord créée à partir du flux
        """
        ln = struct.unpack('<I', fp.read(4))[0]
        data = struct.unpack('%ds' % ln, fp.read(ln))[0]
        return cls(data)