from ..base import Attribute, Record
from ..utils.types import Utf8String
import struct

"""Module pour la gestion des enregistrements d'attributs XML"""

class AttributeRecord(Attribute):
    """Classe pour la gestion des enregistrements d'attributs XML
    
    Cette classe permet de gérer les attributs XML avec préfixe, nom et valeur.
    """
    type: int = 0x05

    def __init__(self, prefix: str, name: str, value: Record) -> None:
        """Initialise un enregistrement d'attribut XML
        
        Args:
            prefix (str): Préfixe de l'attribut
            name (str): Nom de l'attribut
            value (Record): Valeur de l'attribut (doit être un Record)
        """
        self.prefix: str = prefix
        self.name: str = name
        self.value: Record = value

    def to_bytes(self) -> bytes:
        """Convertit l'enregistrement en bytes
        
        Returns:
            bytes: Représentation en bytes de l'enregistrement
        
        Example:
            >>> AttributeRecord('x', 'test', TrueTextRecord()).to_bytes()
            '\x05\x01x\x04test\x86'
        """
        bytes = super(AttributeRecord, self).to_bytes()
        bytes += Utf8String(self.prefix).to_bytes()
        bytes += Utf8String(self.name).to_bytes()
        bytes += self.value.to_bytes()
        return bytes

    def __str__(self) -> str:
        """Convertit l'enregistrement en chaîne XML
        
        Returns:
            str: Représentation XML de l'enregistrement
        """
        return '%s:%s="%s"' % (self.prefix, self.name, str(self.value))
   
    @classmethod
    def parse(cls, fp) -> 'AttributeRecord':
        """Parse un flux de bytes en un enregistrement d'attribut
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            AttributeRecord: Instance d'AttributeRecord créée à partir du flux
        """
        prefix = Utf8String.parse(fp).value
        name = Utf8String.parse(fp).value
        type = struct.unpack('<B', fp.read(1))[0]
        value = Record.records[type].parse(fp)
        return cls(prefix, name, value)