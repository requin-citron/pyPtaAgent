from ..records.ShortElement import ShortElementRecord
from ..utils.types import Utf8String

"""Module pour la gestion des enregistrements d'éléments XML"""

class ElementRecord(ShortElementRecord):
    """Classe pour la gestion des enregistrements d'éléments XML avec préfixe
    
    Cette classe étend ShortElementRecord pour ajouter la gestion des préfixes XML.
    """
    type: int = 0x41

    def __init__(self, prefix: str, name: str, *args, **kwargs) -> None:
        """Initialise un enregistrement d'élément XML
        
        Args:
            prefix (str): Préfixe de l'élément
            name (str): Nom de l'élément
            *args: Arguments additionnels
            **kwargs: Arguments nommés additionnels
        """
        super(ElementRecord, self).__init__(name)
        self.prefix: str = prefix
   
    def to_bytes(self) -> bytes:
        """Convertit l'enregistrement en bytes
        
        Returns:
            bytes: Représentation en bytes de l'enregistrement
        
        Example:
            >>> ElementRecord('x', 'Envelope').to_bytes()
            'A\x01x\x08Envelope'
        """
        pref = Utf8String(self.prefix)
        data = super(ElementRecord, self).to_bytes()
        type = data[0]
        return (type + pref.to_bytes() + data[1:])
   
    def __str__(self) -> str:
        """Convertit l'enregistrement en chaîne XML
        
        Returns:
            str: Représentation XML de l'enregistrement
        """
        return '<%s:%s %s>' % (self.prefix, self.name, 
                ' '.join([str(a) for a in self.attributes]))
   
    @classmethod
    def parse(cls, fp) -> 'ElementRecord':
        """Parse un flux de bytes en un enregistrement d'élément
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            ElementRecord: Instance d'ElementRecord créée à partir du flux
        """
        prefix = Utf8String.parse(fp).value
        name = Utf8String.parse(fp).value
        return cls(prefix, name)