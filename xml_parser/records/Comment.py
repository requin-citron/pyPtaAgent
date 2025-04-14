from ..base import Record
from ..utils.types import Utf8String

"""Module pour la gestion des enregistrements de commentaires XML"""

class CommentRecord(Record):
    """Classe pour la gestion des enregistrements de commentaires XML
    
    Cette classe étend Record pour gérer les commentaires XML.
    """
    type: int = 0x02
    
    def __init__(self, comment: str, *args, **kwargs) -> None:
        """Initialise un enregistrement de commentaire
        
        Args:
            comment (str): Texte du commentaire
            *args: Arguments additionnels
            **kwargs: Arguments nommés additionnels
        """
        self.comment: str = comment

    def to_bytes(self) -> bytes:
        """Convertit l'enregistrement en bytes
        
        Returns:
            bytes: Représentation en bytes de l'enregistrement
        
        Example:
            >>> CommentRecord('test').to_bytes()
            '\x02\x04test'
        """
        string = Utf8String(self.comment)
        return (super(CommentRecord, self).to_bytes() + 
                string.to_bytes())

    def __str__(self) -> str:
        """Convertit l'enregistrement en chaîne XML
        
        Returns:
            str: Représentation XML du commentaire
        
        Example:
            >>> str(CommentRecord('test'))
            '<!-- test -->'
        """
        return '<!-- %s -->' % self.comment

    @classmethod
    def parse(cls, fp) -> 'CommentRecord':
        """Parse un flux de bytes en un enregistrement de commentaire
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            CommentRecord: Instance de CommentRecord créée à partir du flux
        """
        data = Utf8String.parse(fp).value
        return cls(data)
