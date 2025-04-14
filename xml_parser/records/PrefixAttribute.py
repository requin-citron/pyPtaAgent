from ..records.Attribute import AttributeRecord
from ..base import Record
from ..utils.types import Utf8String
import struct

"""Module pour la gestion des attributs avec préfixe XML"""

class PrefixAttributeRecord(AttributeRecord):
    """Classe pour la gestion des attributs avec préfixe XML
    
    Cette classe étend AttributeRecord pour gérer les attributs XML avec préfixe de namespace.
    """
    type: int = 0x08

    def __init__(self, prefix: str, name: str, value: Record) -> None:
        """Initialise un attribut avec préfixe
        
        Args:
            prefix (str): Préfixe du namespace
            name (str): Nom de l'attribut
            value (Record): Valeur de l'attribut
        """
        self.prefix: str = prefix
        self.name: str = name
        self.value: Record = value
        super(PrefixAttributeRecord, self).__init__(self.char, name, value)

    def __str__(self) -> str:
        """Convertit l'attribut en chaîne XML
        
        Returns:
            str: Représentation XML de l'attribut avec préfixe
        """
        return '%s:%s="%s"' % (self.prefix, self.name, str(self.value))

    def to_bytes(self) -> bytes:
        """Convertit l'attribut en bytes
        
        Returns:
            bytes: Représentation en bytes de l'attribut
        """
        string = Utf8String(self.name)
        return (struct.pack('<B', self.type) + string.to_bytes() +
                self.value.to_bytes())

    @classmethod
    def parse(cls, fp) -> 'PrefixAttributeRecord':
        """Parse un flux de bytes en un attribut avec préfixe
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            PrefixAttributeRecord: Instance de PrefixAttributeRecord créée à partir du flux
        """
        name = Utf8String.parse(fp).value
        type = struct.unpack('<B', fp.read(1))[0]
        value = Record.records[type].parse(fp)
        return cls(name, value)
