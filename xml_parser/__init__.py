from .base import Record
from io import BytesIO

from .utils.tools import Net7BitInteger

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

from .records.EndElement import EndElementRecord
from .records.Comment import CommentRecord
from .records.Array import ArrayRecord

Record.add_records((
	# EndElementRecord, #1
	# CommentRecord, #2
	# ArrayRecord, #3
	ShortAttributeRecord, #4
	AttributeRecord, #5
	ShortDictionaryAttributeRecord, #6
	DictionaryAttributeRecord, #7
	ShortXmlnsAttributeRecord, #8
	XmlnsAttributeRecord, #9
	ShortDictionaryXmlnsAttributeRecord, #10
	DictionaryXmlnsAttributeRecord, #11
	ShortElementRecord, #64
	ElementRecord, #65
	ShortDictionaryElementRecord, #66
	DictionaryElementRecord, #67
	ZeroTextRecord, #128
	OneTextRecord, #130
	FalseTextRecord, #132
	TrueTextRecord, #134
	Int8TextRecord, #136
	Int16TextRecord, #138
	Int32TextRecord, #140
	Int64TextRecord, #142
	FloatTextRecord, #144
	DoubleTextRecord, #146
	DecimalTextRecord, #148
	DatetimeTextRecord, #150
	Chars8TextRecord, #152
	Chars16TextRecord, #154
	Chars32TextRecord, #156
	Bytes8TextRecord, #158
	Bytes16TextRecord, #160
	Bytes32TextRecord, #162
	StartListTextRecord, #164
	EndListTextRecord, #166
	EmptyTextRecord, #168
	DictionaryTextRecord, #170
	UniqueIdTextRecord, #172
	TimeSpanTextRecord, #174
	UuidTextRecord, #176
	UInt64TextRecord, #178
	BoolTextRecord, #180
	UnicodeChars8TextRecord, #182
	UnicodeChars16TextRecord, #184
	UnicodeChars32TextRecord, #186
	QNameDictionaryTextRecord #188
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
		envelope = self.buffer.find(b'\x56\x02\x0B')
		inband_elements = []
		if envelope == 0:
			# MC-NBFS
			index = 0
		else:
			# MC-NBFSE
			size_marked, l = Net7BitInteger.decode7bit(self.buffer)
			if size_marked+l != envelope:
				l = 0
			inband_elements = rec.extract_inband_elements(self.buffer[l:envelope])
			index = envelope

		parsed = rec.parse(BytesIO(self.buffer[index:]))
		_, xml = rec.to_string(parsed)

		if envelope != 0:
			pass
			# ToDo
			# Cf: https://github.com/koutto/dotnet-binary-deserializer/blob/master/lib/converter.py#L81-L82
			#partial_stringtable = self.build_partial_stringtable(inband_elements)
			#self.replace_reference_stringtable(partial_stringtable)
		return xml