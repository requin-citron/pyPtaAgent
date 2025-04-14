from ..base import Text
import struct, base64

"""Module pour la gestion des enregistrements de texte binaire (jusqu'à 8 bytes)"""

class Bytes8TextRecord(Text):
    """Classe pour la gestion des enregistrements de texte binaire (jusqu'à 8 bytes)
    
    Cette classe étend Text pour gérer les données binaires de taille limitée à 8 bytes.
    """
    type: int = 0x9E

    def __init__(self, data: bytes) -> None:
        """Initialise un enregistrement de texte binaire
        
        Args:
            data (bytes): Données binaires à stocker (max 8 bytes)
        """
        self.value: bytes = data

    def to_bytes(self) -> bytes:
        """Convertit l'enregistrement en bytes
        
        Returns:
            bytes: Représentation en bytes de l'enregistrement
        """
        bytes = struct.pack('<B', self.type)
        bytes += struct.pack('<B', len(self.value))
        bytes += self.value
        return bytes

    def __str__(self) -> str:
        """Convertit l'enregistrement en chaîne de caractères encodée en base64
        
        Returns:
            str: Représentation en base64 des données binaires
        """
        return base64.b64encode(self.value).decode()

    @classmethod
    def parse(cls, fp) -> 'Bytes8TextRecord':
        """Parse un flux de bytes en un enregistrement de texte binaire
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            Bytes8TextRecord: Instance de Bytes8TextRecord créée à partir du flux
        """
        ln = struct.unpack('<B', fp.read(1))[0]
        data = struct.unpack('%ds' % ln, fp.read(ln))[0]
        return cls(data)