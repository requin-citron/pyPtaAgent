from ..base import Record
from ..records.EndElement import EndElementRecord
from ..utils.types import MultiByteInt31
import struct

"""Module pour la gestion des enregistrements de tableau XML"""

class ArrayRecord(Record):
    """Classe pour la gestion des enregistrements de tableau
    
    Cette classe permet de gérer les tableaux d'éléments XML, y compris leur sérialisation et désérialisation.
    """
    type: int = 0x03

    # Dictionnaire des types de données supportés avec leurs formats
    datatypes: dict = {
        0xB5 : ('BoolTextWithEndElement', 1, '?'),
        0x8B : ('Int16TextWithEndElement', 2, 'h'),
        0x8D : ('Int32TextWithEndElement', 4, 'i'),
        0x8F : ('Int64TextWithEndElement', 8, 'q'),
        0x91 : ('FloatTextWithEndElement', 4, 'f'),
        0x93 : ('DoubleTextWithEndElement', 8, 'd'),
        0x95 : ('DecimalTextWithEndElement', 16, ''),
        0x97 : ('DateTimeTextWithEndElement', 8, ''),
        0xAF : ('TimeSpanTextWithEndElement', 8, ''),
        0xB1 : ('UuidTextWithEndElement', 16, ''),
    }

    def __init__(self, element: Record, recordtype: int, data: list) -> None:
        """Initialise un enregistrement de tableau
        
        Args:
            element (Record): Élément XML qui contiendra les données
            recordtype (int): Type des enregistrements dans le tableau
            data (list): Liste des données à stocker
        """
        self.element: Record = element
        self.recordtype: int = recordtype
        self.count: int = len(data)
        self.data: list = data

    def to_bytes(self) -> bytes:
        """Convertit l'enregistrement en bytes
        
        Returns:
            bytes: Représentation en bytes de l'enregistrement
        """
        bytes = super(ArrayRecord, self).to_bytes()
        bytes += self.element.to_bytes()
        bytes += EndElementRecord().to_bytes()
        bytes += struct.pack('<B', self.recordtype)[0]
        bytes += MultiByteInt31(self.count).to_bytes()
        for data in self.data:
            if type(data) == str:
                bytes += data
            else:
                bytes += data.to_bytes()

        return bytes

    @classmethod
    def parse(cls, fp) -> 'ArrayRecord':
        """Parse un flux de bytes en un enregistrement de tableau
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            ArrayRecord: Instance d'ArrayRecord créée à partir du flux
        """
        element = struct.unpack('<B', fp.read(1))[0]
        element = __records__[element].parse(fp)
        recordtype = struct.unpack('<B', fp.read(1))[0]
        count = MultiByteInt31.parse(fp).value
        data = []
        for i in range(count):
            data.append(__records__[recordtype-1].parse(fp))
        return cls(element, recordtype, data)

    def __str__(self) -> str:
        """Convertit l'enregistrement en chaîne XML
        
        Returns:
            str: Représentation XML de l'enregistrement
        """
        string = ''
        for data in self.data:
            string += str(self.element)
            string += str(data)
            string += '</%s>' % self.element.name

        return string