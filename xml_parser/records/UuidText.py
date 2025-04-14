from ..records.UniqueIdText import UniqueIdTextRecord

class UuidTextRecord(UniqueIdTextRecord):
    type = 0xB0

    def __str__(self):
        return '%08x-%04x-%04x-%02x%02x-%02x%02x%02x%02x%02x%02x' % (
                tuple(self.uuid))