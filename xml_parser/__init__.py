from .base import Record
from io import BytesIO
from .records.ShortDictionnaryElement import ShortDictionaryElementRecord
from .records.ShortElement import ShortElementRecord
from .records.Element import ElementRecord
from .records.DictionaryElement import DictionaryElementRecord
from .records.PrefixElement import PrefixElementRecord
from .records.PrefixDictionaryElement import PrefixDictionaryElementRecord
from .records.ZeroText import ZeroTextRecord
from .records.OneText import OneTextRecord
from .records.FalseText import FalseTextRecord
from .records.TrueText import TrueTextRecord
from .records.Int8Text import Int8TextRecord
from .records.Int16Text import Int16TextRecord
from .records.Int32Text import Int32TextRecord
from .records.Int64Text import Int64TextRecord
from .records.UInt64Text import UInt64TextRecord
from .records.BoolText import BoolTextRecord
from .records.UnicodeChars8Text import UnicodeChars8TextRecord
from .records.UnicodeChars16Text import UnicodeChars16TextRecord
from .records.UnicodeChars32Text import UnicodeChars32TextRecord
from .records.QNameDictionaryText import QNameDictionaryTextRecord
from .records.FloatText import FloatTextRecord
from .records.DoubleText import DoubleTextRecord
from .records.DecimalText import DecimalTextRecord
from .records.DatetimeText import DatetimeTextRecord
from .records.Chars8Text import Chars8TextRecord
from .records.Chars16Text import Chars16TextRecord
from .records.Chars32Text import Chars32TextRecord
from .records.UniqueIdText import UniqueIdTextRecord
from .records.UuidText import UuidTextRecord
from .records.Bytes8Text import Bytes8TextRecord
from .records.Bytes16Text import Bytes16TextRecord
from .records.Bytes32Text import Bytes32TextRecord
from .records.StartListText import StartListTextRecord
from .records.EndListText import EndListTextRecord
from .records.EmptyText import EmptyTextRecord
from .records.TimeSpanText import TimeSpanTextRecord
from .records.DictionaryText import DictionaryTextRecord

from .records.ShortAttribute import ShortAttributeRecord
from .records.Attribute import AttributeRecord
from .records.ShortDictionaryAttribute import ShortDictionaryAttributeRecord
from .records.DictionaryAttribute import DictionaryAttributeRecord
from .records.ShortDictionaryXmlnsAttribute import ShortDictionaryXmlnsAttributeRecord
from .records.DictionaryXmlnsAttribute import DictionaryXmlnsAttributeRecord
from .records.ShortXmlnsAttribute import ShortXmlnsAttributeRecord
from .records.XmlnsAttribute import XmlnsAttributeRecord
from .records.PrefixDictionaryAttribute import PrefixDictionaryAttributeRecord
from .records.PrefixAttribute import PrefixAttributeRecord

Record.add_records((
    ShortDictionaryElementRecord,
    ShortElementRecord,
    ElementRecord,
    DictionaryElementRecord,

    ZeroTextRecord,
    OneTextRecord,
    FalseTextRecord,
    TrueTextRecord,
    Int8TextRecord,
    Int16TextRecord,
    Int32TextRecord,
    Int64TextRecord,
    UInt64TextRecord,
    BoolTextRecord,
    UnicodeChars8TextRecord,
    UnicodeChars16TextRecord,
    UnicodeChars32TextRecord,
    QNameDictionaryTextRecord,
    FloatTextRecord,
    DoubleTextRecord,
    DecimalTextRecord,
    DatetimeTextRecord,
    Chars8TextRecord,
    Chars16TextRecord,
    Chars32TextRecord,
    UniqueIdTextRecord,
    UuidTextRecord,
    Bytes8TextRecord,
    Bytes16TextRecord,
    Bytes32TextRecord,
    StartListTextRecord,
    EndListTextRecord,
    EmptyTextRecord,
    TimeSpanTextRecord,
    DictionaryTextRecord,

    ShortAttributeRecord,
    AttributeRecord,
    ShortDictionaryAttributeRecord,
    DictionaryAttributeRecord,
    ShortDictionaryXmlnsAttributeRecord,
    DictionaryXmlnsAttributeRecord,
    ShortXmlnsAttributeRecord,
    XmlnsAttributeRecord
))

__records__ = []
for c in range(0x44, 0x5D + 1):
    char = chr(c - 0x44 + ord('a'))
    __records__.append(type(
        'PrefixDictionaryElement' + char.upper() + 'Record',
        (PrefixDictionaryElementRecord,),
        dict(type=c,char=char)
    ))

for c in range(0x5E, 0x77 + 1):
    char = chr(c - 0x5E + ord('a'))
    __records__.append(type(
           'PrefixElement' + char.upper() + 'Record',
           (PrefixElementRecord,),
           dict(type=c, char=char)
    ))
    
for c in range(0x0C, 0x25 + 1):
    char = chr(c - 0x0C + ord('a'))
    __records__.append(type(
           'PrefixDictionaryAttribute' + char.upper() + 'Record',
           (PrefixDictionaryAttributeRecord,),
           dict(type=c,char=char)
    ))

for c in range(0x26, 0x3F + 1):
    char = chr(c - 0x26 + ord('a'))
    __records__.append(type(
           'PrefixAttribute' + char.upper() + 'Record',
           (PrefixAttributeRecord,),
           dict(type=c,char=char)
    ))
    

Record.add_records(__records__)

class XmlParser:
    """Classe principale pour le parsing XML
    
    Cette classe gère le parsing d'un flux de bytes en une structure XML.
    """
    
    def __init__(self, buffer: BytesIO) -> None:
        """Initialise le parser XML
        
        Args:
            buffer (BytesIO): Flux de bytes à parser
        """
        self.buffer: BytesIO = buffer

    def unserialize(self) -> str:
        """Parse le flux de bytes en une structure XML
        
        Returns:
            Any: Structure XML parsee
        """
        rec = Record()
        parsed = rec.parse(self.buffer)
        _, xml = rec.to_string(parsed)
        return xml