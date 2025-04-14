import struct


class MultiByteInt31(object):

    def __init__(self, *args):
        self.value = args[0] if len(args) else None
    
    def to_bytes(self):
        """
        >>> MultiByteInt31(268435456).to_bytes()
        '\\x80\\x80\\x80\\x80\\x01'
        >>> MultiByteInt31(0x7f).to_bytes()
        '\\x7f'
        >>> MultiByteInt31(0x3fff).to_bytes()
        '\\xff\\x7f'
        >>> MultiByteInt31(0x1fffff).to_bytes()
        '\\xff\\xff\\x7f'
        >>> MultiByteInt31(0xfffffff).to_bytes()
        '\\xff\\xff\\xff\\x7f'
        >>> MultiByteInt31(0x3fffffff).to_bytes()
        '\\xff\\xff\\xff\\xff\\x03'
        """
        value_a = self.value & 0x7F
        value_b = (self.value >>  7) & 0x7F
        value_c = (self.value >> 14) & 0x7F
        value_d = (self.value >> 21) & 0x7F
        value_e = (self.value >> 28) & 0x03
        if value_e != 0:
            return struct.pack('<BBBBB',
                    value_a | 0x80,
                    value_b | 0x80,
                    value_c | 0x80,
                    value_d | 0x80,
                    value_e)
        elif value_d != 0:
            return struct.pack('<BBBB',
                    value_a | 0x80,
                    value_b | 0x80,
                    value_c | 0x80,
                    value_d)
        elif value_c != 0:
            return struct.pack('<BBB',
                    value_a | 0x80,
                    value_b | 0x80,
                    value_c)
        elif value_b != 0:
            return struct.pack('<BB',
                    value_a | 0x80,
                    value_b)
        else:
            return struct.pack('<B',
                    value_a)

    def __str__(self):
        return str(self.value)

    @classmethod
    def parse(cls, fp):
        v = 0
        for pos in range(4):
            b = fp.read(1)
            value = struct.unpack('<B', b)[0]
            v |= (value & 0x7F) << 7*pos
            if not value & 0x80:
                break
        return cls(v)

class Utf8String(object):

    def __init__(self, *args):
        self.value = args[0] if len(args) else None

    def to_bytes(self):
        """
        >>> Utf8String(u"abc").to_bytes()
        '\\x03\x61\x62\x63'
        >>> Utf8String(u"\xfcber").to_bytes()
        '\\x05\\xc3\\xbcber'
        >>> Utf8String("\\xc3\\xbcber".decode('utf-8')).to_bytes()
        '\\x05\\xc3\\xbcber'
        """
        data  = self.value.encode('utf-8')
        strlen = len(data)
        return MultiByteInt31(strlen).to_bytes() + data

    def __str__(self):
        return self.value.decode('latin1')

    def __unicode__(self):
	    return self.value

    @classmethod
    def parse(cls, fp):
        """
        >>> from StringIO import StringIO as io
        >>> fp = io("\\x05\\xc3\\xbcber")
        >>> s = Utf8String.parse(fp)
        >>> s.to_bytes()
            '\\x05\\xc3\\xbcber'
        >>> print str(s)
        """
        length = struct.unpack('<B', fp.read(1))[0]
        return cls(fp.read(length).decode('utf-8'))