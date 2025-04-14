from ..base import Text
import struct
from typing import Union, List, Tuple

"""Module pour la gestion des enregistrements de texte UUID"""

class UniqueIdTextRecord(Text):
    """Classe pour la gestion des enregistrements de texte UUID
    
    Cette classe étend Text pour gérer les valeurs UUID au format standard.
    """
    type: int = 0xAC

    def __init__(self, uuid: Union[str, List[int], Tuple[int, ...]]) -> None:
        """Initialise un enregistrement de texte UUID
        
        Args:
            uuid (Union[str, List[int], Tuple[int, ...]]): UUID à stocker
                - Si str: Format 'urn:uuid:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
                - Si List[int] ou Tuple[int]: Liste des 10 composants de l'UUID
        """
        if isinstance(uuid, (list, tuple)):
            self.uuid: List[int] = list(uuid)
        else:
            # Nettoyage du format urn:uuid: si présent
            if uuid.startswith('urn:uuid:'):
                uuid = uuid[9:]
            # Conversion du format xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
            uuid_parts = uuid.split('-')
            # Réorganisation des composants selon le format standard
            tmp = uuid_parts[0:3]  # Les 3 premiers groupes
            tmp.append(uuid_parts[3][0:2])  # Les 2 premiers octets du 4ème groupe
            tmp.append(uuid_parts[3][2:])   # Les 2 derniers octets du 4ème groupe
            # Le 5ème groupe est divisé en 5 parties de 2 octets
            tmp.append(uuid_parts[4][0:2])
            tmp.append(uuid_parts[4][2:4])
            tmp.append(uuid_parts[4][4:6])
            tmp.append(uuid_parts[4][6:8])
            tmp.append(uuid_parts[4][8:10])
            tmp.append(uuid_parts[4][10:])
            self.uuid = [int(s, 16) for s in tmp]

    def to_bytes(self) -> bytes:
        """Convertit l'enregistrement en bytes
        
        Returns:
            bytes: Représentation en bytes de l'enregistrement
        
        Example:
            >>> UniqueIdTextRecord('urn:uuid:33221100-5544-7766-8899-aabbccddeeff').to_bytes()
            '\xac\x00\x11\x22\x33\x44\x55\x66\x77\x88\x99\xaa\xbb\xcc\xdd\xee\xff'
        """
        bytes = super(UniqueIdTextRecord, self).to_bytes()
        bytes += struct.pack('<IHHBBBBBBBB', *self.uuid)
        return bytes

    def __str__(self) -> str:
        """Convertit l'enregistrement en chaîne de caractères
        
        Returns:
            str: Représentation textuelle du UUID au format standard
        """
        return 'urn:uuid:%08x-%04x-%04x-%02x%02x-%02x%02x%02x%02x%02x%02x' % (
                tuple(self.uuid))

    @classmethod
    def parse(cls, fp) -> 'UniqueIdTextRecord':
        """Parse un flux de bytes en un enregistrement de texte UUID
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            UniqueIdTextRecord: Instance de UniqueIdTextRecord créée à partir du flux
        """
        uuid = struct.unpack('<IHHBBBBBBBB', fp.read(16))
        return cls(uuid)