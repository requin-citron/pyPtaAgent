from ..records.Bytes8Text import Bytes8TextRecord
import struct, base64

"""Module pour la gestion des enregistrements de texte binaire (jusqu'à 16 bytes)"""

class Bytes16TextRecord(Bytes8TextRecord):
    """Classe pour la gestion des enregistrements de texte binaire (jusqu'à 16 bytes)
    
    Cette classe étend Bytes8TextRecord pour gérer les données binaires de taille limitée à 16 bytes.
    """
    type: int = 0xA0

    def __init__(self, data: bytes) -> None:
        """Initialise un enregistrement de texte binaire
        
        Args:
            data (bytes): Données binaires à stocker (max 16 bytes)
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
        bytes += struct.pack('<H', len(self.value))
        bytes += self.value
        return bytes

    @classmethod
    def parse(cls, fp) -> 'Bytes16TextRecord':
        """Parse un flux de bytes en un enregistrement de texte binaire
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            Bytes16TextRecord: Instance de Bytes16TextRecord créée à partir du flux
        """
        ln = struct.unpack('<H', fp.read(2))[0]
        data = struct.unpack('%ds' % ln, fp.read(ln))[0]
        return cls(data)