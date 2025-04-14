from ..base import Text

"""Module pour la gestion des enregistrements de texte booléen faux"""

class FalseTextRecord(Text):
    """Classe pour la gestion des enregistrements de texte booléen faux
    
    Cette classe étend Text pour gérer les valeurs booléennes fausses.
    """
    type: int = 0x84

    def __str__(self) -> str:
        """Convertit l'enregistrement en chaîne de caractères
        
        Returns:
            str: Représentation textuelle de la valeur booléenne
        """
        return 'false'

    @classmethod
    def parse(cls, fp) -> 'FalseTextRecord':
        """Parse un flux de bytes en un enregistrement de texte booléen faux
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            FalseTextRecord: Instance de FalseTextRecord créée à partir du flux
        """
        return cls()