from ..base import Text
import struct
from html.entities import codepoint2name

"""Module pour la gestion des enregistrements de texte (jusqu'à 8 caractères)"""

def escapecp(cp: int) -> str:
    """Convertit un codepoint en entité HTML si possible
    
    Args:
        cp (int): Codepoint Unicode à convertir
        
    Returns:
        str: Entité HTML ou caractère original
    """
    return '&%s;' % codepoint2name[cp] if (cp in codepoint2name) else chr(cp)

def escape(text: str) -> str:
    """Échappe les caractères spéciaux en entités HTML
    
    Args:
        text (str): Texte à échapper
        
    Returns:
        str: Texte avec les caractères spéciaux échappés en entités HTML
    """
    newtext = ''
    for c in text:
        newtext += escapecp(ord(c))
    return newtext

class Chars8TextRecord(Text):
    """Classe pour la gestion des enregistrements de texte (jusqu'à 8 caractères)
    
    Cette classe étend Text pour gérer les chaînes de caractères de taille limitée à 8 caractères.
    """
    type: int = 0x98

    def __init__(self, value: str) -> None:
        """Initialise un enregistrement de texte
        
        Args:
            value (str): Texte à stocker
        """
        if isinstance(value, str):
            self.value: str = value
        else:
            self.value: str = str(value)

    def __str__(self) -> str:
        """Convertit l'enregistrement en chaîne de caractères avec échappement HTML
        
        Returns:
            str: Représentation textuelle avec les caractères spéciaux échappés
        """
        return escape(self.value)

    def to_bytes(self) -> bytes:
        """Convertit l'enregistrement en bytes
        
        Returns:
            bytes: Représentation en bytes de l'enregistrement
        """
        data = self.value.encode('utf-8')
        bytes = struct.pack('<B', self.type)
        bytes += struct.pack('<B', len(data))
        bytes += data
        return bytes

    @classmethod
    def parse(cls, fp) -> 'Chars8TextRecord':
        """Parse un flux de bytes en un enregistrement de texte
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            Chars8TextRecord: Instance de Chars8TextRecord créée à partir du flux
        """
        ln = struct.unpack('<B', fp.read(1))[0]
        value = fp.read(ln).decode('utf-8')
        return cls(value)