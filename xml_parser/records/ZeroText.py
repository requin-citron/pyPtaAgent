from ..base import Text

class ZeroTextRecord(Text):
    type = 0x80

    def __str__(self):
        return '0'

    @classmethod
    def parse(cls, fp):
        return cls()