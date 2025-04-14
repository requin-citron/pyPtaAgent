from ..base import Text

"""Module pour la gestion des enregistrements de texte '1'"""

class OneTextRecord(Text):
    """Classe pour la gestion des enregistrements de texte '1'
    
    Cette classe étend Text pour gérer la valeur constante '1' de manière optimisée.
    """
    type: int = 0x82

    def __str__(self) -> str:
        """Convertit l'enregistrement en chaîne de caractères
        
        Returns:
            str: Représentation textuelle de la valeur '1'
        """
        return '1'

    @classmethod
    def parse(cls, fp) -> 'OneTextRecord':
        """Parse un flux de bytes en un enregistrement de texte '1'
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            OneTextRecord: Instance d'OneTextRecord créée à partir du flux
        """
        return cls()