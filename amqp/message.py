from .paquet import *

class AMQPList(AMQPItem):
    def __init__(self):
        super().__init__()
        self.items = []

    def add(self, item):
        self.items.append(item)

    def to_byte_array(self):
        if not self.items:
            self._write_byte(0x45)
        else:
            buffer = io.BytesIO()
            for item in self.items:
                buffer.write(item.to_byte_array())
            elements = buffer.getvalue()
            self._write_list_header(len(elements), len(self.items))
            self._write_byte_array(elements)
        
        return self._get_bytes()

    def _write_list_header(self, element_size, count):
        if count < 255 and element_size < 255:
            self._write_byte(0xC0)
            self._write_byte(element_size + 1)
            self._write_byte(count)
        else:
            self._write_byte(0xD0)
            self._write_int(element_size + 4, 'I')
            self._write_int(count, 'I')

class AMQPProtocolHeader(AMQPItem):
    def __init__(self, type, major=1, minor=0, revision=0):
        super().__init__()
        self._write_protocol_header(type, major, minor, revision)

    def _write_protocol_header(self, type, major, minor, revision):
        self._write_byte_array(b"AMQP")
        self._write_byte(type)
        self._write_byte(major)
        self._write_byte(minor)
        self._write_byte(revision)

class SASLInit(AMQPMessage):
    def __init__(self, mechanics=SASLMechanics.EXTERNAL):
        super().__init__()
        self._construct_sasl_init_message(mechanics)

    def _construct_sasl_init_message(self, mechanics):
        mechanics_values = {
            SASLMechanics.EXTERNAL: "EXTERNAL",
            SASLMechanics.MSSBCBS: "MSSBCBS",
            SASLMechanics.PLAIN: "PLAIN",
            SASLMechanics.ANONYMOUS: "ANONYMOUS"
        }
        amqp_list = AMQPList()
        amqp_list.add(AMQPSymbol(mechanics_values[mechanics]))
        amqp_list.add(AMQPNull())
        amqp_list.add(AMQPNull())
        self.init(AMQPMessageType.SASLInit, amqp_list)


class AMQPOpen(AMQPMessage):
    def __init__(self, container_id, host_name):
        super().__init__()
        amqp_list = AMQPList()
        amqp_list.add(AMQPString(container_id))
        amqp_list.add(AMQPString(host_name))
        amqp_list.add(AMQPUInt(65536))      # Max Frame Size
        amqp_list.add(AMQPUShort(8191))     # Channel max
        amqp_list.add(AMQPNull())           # Idle timeout in milliseconds
        amqp_list.add(AMQPNull())           # Outgoing locales
        amqp_list.add(AMQPNull())           # Incoming locales
        amqp_list.add(AMQPNull())           # Offered capabilities
        amqp_list.add(AMQPNull())           # Desired capabilities
        amqp_list.add(AMQPNull())           # Properties
        self.init(AMQPMessageType.AMQPOpen, amqp_list)

class AMQPBegin(AMQPMessage):
    def __init__(self):
        super().__init__()
        amqp_list = AMQPList()
        amqp_list.add(AMQPNull())           # Remote channel
        amqp_list.add(AMQPSmallUInt(1))     # Next outgoing id
        amqp_list.add(AMQPUInt(5000))       # Incoming window
        amqp_list.add(AMQPUInt(5000))       # Outgoing window
        amqp_list.add(AMQPUInt(262143))     # Handle max
        amqp_list.add(AMQPNull())           # Offered capabilities
        amqp_list.add(AMQPNull())           # Desired capabilities
        amqp_list.add(AMQPNull())           # Properties
        self.init(AMQPMessageType.AMQPBegin, amqp_list)

class AMQPAttach(AMQPMessage):
    def __init__(self, link_name, service_bus, SAS, tracking_id, is_input, handle):
        super().__init__()
        
        if is_input:
            direction = AMQPTrue()
            s_list = AMQPList()
            s_list.add(AMQPString(service_bus))
            [s_list.add(AMQPNull()) for _ in range(10)]
            source = AMQPConstructor(AMQPSmallULong(0x28), s_list)

            t_list = AMQPList()
            [t_list.add(AMQPNull()) for _ in range(7)]
            target = AMQPConstructor(AMQPSmallULong(0x29), t_list)
        else:
            direction = AMQPFalse()

            s_list = AMQPList()
            [s_list.add(AMQPNull()) for _ in range(11)]
            source = AMQPConstructor(AMQPSmallULong(0x28), s_list)

            t_list = AMQPList()
            t_list.add(AMQPString(service_bus))
            [t_list.add(AMQPNull()) for _ in range(6)]
            target = AMQPConstructor(AMQPSmallULong(0x29), t_list)

        properties = AMQPMap()
        properties.add(AMQPSymbol("com.microsoft:swt"), AMQPString(SAS))
        properties.add(AMQPSymbol("com.microsoft:client-agent"), AMQPString("ServiceBus/3.0.51093.14;"))
        properties.add(AMQPSymbol("com.microsoft:dynamic-relay"), AMQPFalse())
        properties.add(AMQPSymbol("com.microsoft:listener-type"), AMQPString("RelayedConnection"))
        properties.add(AMQPSymbol("com.microsoft:tracking-id"), AMQPString(tracking_id))

        amqp_list = AMQPList()
        amqp_list.add(AMQPString(link_name))    # Link name
        amqp_list.add(AMQPSmallUInt(handle))    # Handle
        amqp_list.add(direction)                # Direction       
        amqp_list.add(AMQPNull())               # snd-settle-mode
        amqp_list.add(AMQPNull())               # rcv-settle-mode
        amqp_list.add(source)                   # source
        amqp_list.add(target)                   # target
        amqp_list.add(AMQPNull())               # unsettled
        amqp_list.add(AMQPNull())               # incomplete-unsettled
        amqp_list.add(AMQPNull())               # initial-delivery-count
        amqp_list.add(AMQPNull())               # max-message-size
        amqp_list.add(AMQPNull())               # offered-capabilities
        amqp_list.add(AMQPNull())               # desired-capabilities
        amqp_list.add(properties)               # Properties
        self.init(AMQPMessageType.AMQPAttach, amqp_list)

class AMQPDisposition(AMQPMessage):
    def __init__(self, is_input, state, first=0):
        # Ref: http://docs.oasis-open.org/amqp/core/v1.0/os/amqp-core-transport-v1.0-os.html#type-disposition
        super().__init__()

        amqp_list = AMQPList()
        amqp_list.add(AMQPTrue() if is_input else AMQPFalse())              # direction
        amqp_list.add(AMQPSmallUInt(first))                                 # first
        amqp_list.add(AMQPNull())                                           # last
        amqp_list.add(AMQPTrue())                                           # settled
        amqp_list.add(AMQPConstructor( AMQPSmallULong(state), AMQPList() )) # state
        amqp_list.add(AMQPNull())                                           # Properties
        self.init(AMQPMessageType.AMQPDisposition, amqp_list)

class AMQPFlow(AMQPMessage):
    def __init__(self, handle, next_incoming_id=1, next_outgoing_id=1, link_credit=1000):
        super().__init__()
        amqp_list = AMQPList()
        amqp_list.add(AMQPSmallUInt(next_incoming_id))  # next-incoming-id
        amqp_list.add(AMQPUInt(5000))                   # incoming-window
        amqp_list.add(AMQPSmallUInt(next_outgoing_id))  # next-outgoing-id
        amqp_list.add(AMQPUInt(5000))                   # outgoing-window
        amqp_list.add(AMQPSmallUInt(handle))            # handle
        amqp_list.add(AMQPSmallUInt(0))                 # delivery-count
        amqp_list.add(AMQPUInt(link_credit))            # link-credit
        amqp_list.add(AMQPSmallUInt(0))                 # available
        amqp_list.add(AMQPNull())                       # Drain
        amqp_list.add(AMQPFalse())                      # Echo
        amqp_list.add(AMQPNull())                       # Properties
        self.init(AMQPMessageType.AMQPFlow, amqp_list)