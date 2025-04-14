from ..base import Text
import datetime, struct

"""Module pour la gestion des enregistrements de texte date/heure"""

class DatetimeTextRecord(Text):
    """Classe pour la gestion des enregistrements de texte date/heure
    
    Cette classe étend Text pour gérer les dates/heure avec timezone.
    """
    type: int = 0x96

    def __init__(self, value: int, tz: int) -> None:
        """Initialise un enregistrement de texte date/heure
        
        Args:
            value (int): Nombre de ticks depuis l'époque
            tz (int): Timezone (0-3)
        """
        self.value: int = value
        self.tz: int = tz

    def __str__(self) -> str:
        """Convertit l'enregistrement en chaîne ISO8601
        
        Returns:
            str: Représentation ISO8601 de la date/heure
        
        Examples:
            >>> str(DatetimeTextRecord(621355968000000000,0))
            '1970-01-01T00:00:00'
            >>> str(DatetimeTextRecord(0,0))
            '0001-01-01T00:00:00'
        """
        ticks = self.value
        dt = (datetime.datetime(1, 1, 1) +
                datetime.timedelta(microseconds=ticks/10))
        return dt.isoformat()

    def to_bytes(self) -> bytes:
        """Convertit l'enregistrement en bytes
        
        Returns:
            bytes: Représentation en bytes de l'enregistrement
        """
        bytes = super(DatetimeTextRecord, self).to_bytes()
        bytes += struct.pack('<Q',
                (self.tz & 3) | (self.value & 0x1FFFFFFFFFFFFFFF) << 2)
        return bytes

    @classmethod
    def parse(cls, fp) -> 'DatetimeTextRecord':
        """Parse un flux de bytes en un enregistrement de texte date/heure
        
        Args:
            fp: Flux de bytes à parser
            
        Returns:
            DatetimeTextRecord: Instance de DatetimeTextRecord créée à partir du flux
        """
        data = struct.unpack('<Q', fp.read(8))[0]
        tz = data & 3
        value = data >> 2
        return DatetimeTextRecord(value, tz)