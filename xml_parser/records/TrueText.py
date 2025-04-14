from ..base import Text

"""Module pour la gestion des enregistrements de texte booléen 'true'"""

class TrueTextRecord(Text):
    """Classe pour la gestion des enregistrements de texte booléen 'true'
    
    Cette classe étend Text pour gérer la valeur constante 'true' de manière optimisée.
    """
    type: int = 0x86

    def __str__(self) -> str:
        """Convertit l'enregistrement en chaîne de caractères
        
        Returns:
            str: Représentation textuelle de la valeur 'true'
        """
        return 'true'

    @classmethod
    def parse(cls, fp) -> 'TrueTextRecord':
        """Parse un flux de bytes en un enregistrement de texte booléen 'true'
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            TrueTextRecord: Instance de TrueTextRecord créée à partir du flux
        """
        return cls()