from amqp.parser_type import ParsedMessage, parse_amqp_item, parse_amqp_list
from xml_parser import XmlParser

import base64, io
from typing import Union
import xml.etree.ElementTree as ET

def parse_amqp_open(message, bytes_data, pos):
    message["Type"] = "AMQP Open"
    content, pos = parse_amqp_item(bytes_data, pos)
    message.add("ContainerId", content[0])
    message.add("HostName", content[1])
    message.add("MaxFrameSize", content[2])
    message.add("ChannelMax", content[3])
    message.add("IdleTimeOut", content[4])
    message.add("OutgoingLocales", content[5])
    message.add("IncomingLocales", content[6])
    message.add("OfferedCapabilities", content[7])
    message.add("DesiredCapabilities", content[8])
    message.add("Properties", content[9])

def parse_amqp_begin(message, bytes_data, pos):
    message["Type"] = "AMQP Begin"
    content, pos = parse_amqp_item(bytes_data, pos)
    message.add("RemoteChannel", content[0])
    message.add("NextOutgoingId", content[1])
    message.add("IncomingWindow", content[2])
    message.add("OutgoingWindow", content[3])
    message.add("HandleMax", content[4])
    message.add("OfferedCapabilities", content[5])
    message.add("DesiredCapabilities", content[6])
    message.add("Properties", content[7])

def parse_amqp_attach(message, bytes_data, pos):
    message["Type"] = "AMQP Attach"
    content, pos = parse_amqp_item(bytes_data, pos)
    message.add("Name", content[0])
    message.add("Handle", content[1])    
    target_pos = 0
    message.add("Direction", "out")
    if content[2] == True:
        message["Direction"] = "in"
        target_pos = -1

    target = content[6 + target_pos]
    if target:
        message.add("Target", target.get("Target List", [None])[0])
    if len(content) > 13 and content[13]:
        tracking_id = content[13].get("TrackingId", None)
        if tracking_id:
            message.add("TrackingId", tracking_id)

def parse_amqp_flow(message, bytes_data, pos):
    message["Type"] = "AMQP Flow"
    content, pos = parse_amqp_item(bytes_data, pos)
    message.add("NextIncomingId", content[0])
    message.add("IncomingWindow", content[1])
    message.add("NextOutgoingId", content[2])
    message.add("OutgoingWindow", content[3])
    message.add("Handle", content[4])
    message.add("DeliveryCount", content[5])
    message.add("LinkCredit", content[6])
    message.add("Available", content[7])
    message.add("Drain", content[8])
    message.add("Echo", content[9])
    message.add("Properties", content[10])

def parse_amqp_transfer(message, bytes_data, pos):
    message["Type"] = "AMQP Transfer"
    content, pos = parse_amqp_item(bytes_data, pos)
    message.add("Handle", content[0])
    message.add("DeliveryId", content[1])
    message.add("DeliveryTag", content[2])
    message.add("MessageFormat", content[3])
    message.add("Settled", content[4])
    message.add("More", content[5])
    message.add("RcvSettleMode", content[6])
    message.add("State", content[7])
    message.add("Resume", content[8])
    message.add("Aborted", content[9])
    message.add("Batchable", content[10])

def parse_amqp_disposition(message, bytes_data, pos):
    message["Type"] = "AMQP Disposition"
    content, pos = parse_amqp_item(bytes_data, pos)
    message.add("Role", content[0])
    message.add("First", content[1])
    message.add("Last", content[2])
    message.add("Settled", content[3])
    message.add("State", content[4])
    message.add("Batchable", content[5])

def parse_amqp_detach(message, bytes_data, pos):
    message["Type"] = "AMQP Detach"
    content, pos = parse_amqp_item(bytes_data, pos)
    message.add("Handle", content[0])
    message.add("Closed", content[1])
    if len(content) > 2:
        message.add("Error", content[2])

def parse_amqp_end(message, bytes_data, pos):
    message["Type"] = "AMQP End"
    content, pos = parse_amqp_item(bytes_data, pos)
    if content:
        message.add("Error", parse_amqp_error(content[0]))

def parse_amqp_close(message, bytes_data, pos):
    message["Type"] = "AMQP Close"
    content, pos = parse_amqp_item(bytes_data, pos)
    if content:
        message.add("Error", content[0])

def parse_amqp_error(error):
    ret_val = error
    if error is not None and isinstance(error, (list, tuple)):
        if len(error) > 0 and isinstance(error[0], (list, tuple)):
            ret_val = error[0][0] if len(error[0]) > 0 else None
    return ret_val

def parse_amqp_frame(message_bytes: bytes) -> ParsedMessage:
    size_bytes = message_bytes[:4]
    DOff = message_bytes[4]
    message = ParsedMessage(message_bytes)
    message.add("Size", int.from_bytes(size_bytes, byteorder='big'))
    message.add("DOFF", DOff)
    message.add("Extended Header", message_bytes[8:8+DOff*4])
    
    pos = DOff * 4 + 2
    
    if message_bytes[5] == 0x00:
        message["Type"] = "AMQP"
        channel_bytes = message_bytes[6:8]
        channel = int.from_bytes(channel_bytes, byteorder='big')
        message.add("Channel", channel)

        pos += 1
        AMQP_TYPE_PARSERS = {
            0x10: parse_amqp_open,
            0x11: parse_amqp_begin,
            0x12: parse_amqp_attach,
            0x13: parse_amqp_flow,
            0x14: parse_amqp_transfer,
            0x15: parse_amqp_disposition,
            0x16: parse_amqp_detach,
            0x17: parse_amqp_end,
            0x18: parse_amqp_close,
        }        
        frame_type = message_bytes[pos-1]
        if frame_type in AMQP_TYPE_PARSERS:
            AMQP_TYPE_PARSERS[frame_type](message, message_bytes, pos)
    
    else:
        pos += 1
        if message_bytes[pos-1] == 0x40:
            message.add("Type", "SASL Mechanisms")
            content, pos = parse_amqp_list(message_bytes, pos)
            message.add("Content", content)
        elif message_bytes[pos-1] == 0x41:
            content, pos = parse_amqp_list(message_bytes, pos)
            sasl_outcome = {
                0: "ok",
                1: "auth",
                2: "sys",
                3: "sys-perm",
                4: "sys-temp"
            }
            message.add("Type", "SASL Outcome")
            if len(content) > 0:
                status_key = content[0]
                status = sasl_outcome.get(status_key, "Unknown")
                message.add("Status", status)
            if len(content) > 1:
                base64_str = content[1]
                try:
                    decoded_message = base64.b64decode(base64_str).decode('ascii')
                    message.add("Message", decoded_message)
                except Exception as e:
                    message.add("Message", f"Error decoding base64: {str(e)}")

    return message


def parse_bus_message(message_bytes: bytes) -> Union[None, ParsedMessage]:
    if message_bytes is None:
        return None
    if message_bytes[:2] == b'\x41\x4d':
        message = ParsedMessage(message_bytes)
        type_str = ""
        if message_bytes[4] == 0 or  message_bytes[4] == 1:
            type_str = "AMQP"
        elif message_bytes[4] == 2:
            type_str = "TLS"
        elif message_bytes[4] == 3:
            type_str = "SASL"
        message.add("Type", f"Protocol {type_str}")
        message.add("Protocol", message_bytes[4])
        message.add("Major", message_bytes[5])
        message.add("Minor", message_bytes[6])
        message.add("Revision", message_bytes[7])
        return message
    else:
        return parse_amqp_frame(message_bytes)


def parse_relay_binary_xml(bytes_data, no_session={}):        
    msg = ParsedMessage(bytes_data)
    msg.add("Type", "RelayMessage")
    xml_string = XmlParser(io.BytesIO(bytes_data)).unserialize()
    try:
        xml_root = ET.fromstring(xml_string)
        namespaces = {
            'a': "http://www.w3.org/2005/08/addressing",
            'b': "http://schemas.datacontract.org/2004/07/Microsoft.ApplicationProxy.Common.SignalingDataModel",
            'netrm': "http://schemas.microsoft.com/ws/2006/05/rm",
            'i': "http://www.w3.org/2001/XMLSchema-instance",
            'r': "http://schemas.xmlsoap.org/ws/2005/02/rm",
            's': "http://www.w3.org/2003/05/soap-envelope",
            'sb': "http://schemas.microsoft.com/netservices/2009/05/servicebus/relayedconnect"
        }
        header_node = xml_root.find('.//s:Header', namespaces)
        if header_node is not None:
            for header in header_node:
                msg.add(header.tag.split('}')[-1], header.text)

        body_node = xml_root.find('.//s:Body', namespaces)
        if body_node is not None and body_node.text:
            msg.add("Body", body_node.text)

        if "Action" in msg.info:
            msg.add("Type", msg.info["Action"])

    except ET.ParseError as e:
        if session and session.get(0, "") == "Ping":
            msg.add("Type", "Ping")

    message_type = msg.info.get("Type", "")
    if message_type == "OnewaySend":
        """
        <s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" xmlns:a="http://www.w3.org/2005/08/addressing">
            <s:Header>
                <a:Action s:mustUnderstand="1">OnewaySend</a:Action>
                <RelayVia xmlns="http://schemas.microsoft.com/netservices/2009/05/servicebus/connect">sb://his-nam1-scus2.servicebus.windows.net/[redacted]_17d93d40-1389-4f69-b6f6-dcaedfdc4bb7_reliable</RelayVia>
                <a:MessageID>655e645f-7e22-4368-bf77-c7a17520f929_G7</a:MessageID>
                <a:To s:mustUnderstand="1">sb://his-nam1-scus2.servicebus.windows.net/[redacted]_17d93d40-1389-4f69-b6f6-dcaedfdc4bb7_reliable</a:To>
            </s:Header>
            <s:Body>VgILAXME[redacted]QBAQE=</s:Body>
        </s:Envelope>
        """
        body = msg.info.get("Body", "")
        bin_body = base64.b64decode(body.encode())
        relayed_xml_string = XmlParser(io.BytesIO(bin_body)).unserialize()
        relayed_xml_root = ET.fromstring(relayed_xml_string)
        """
        <s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" xmlns:a="http://www.w3.org/2005/08/addressing">
            <s:Header>
                <a:Action s:mustUnderstand="1">http://schemas.microsoft.com/netservices/2009/05/servicebus/relayedconnect/RelayedConnect</a:Action>
                <a:To s:mustUnderstand="1">sb://his-nam1-ncus1.servicebus.windows.net/[redacted]_17d93d40-1389-4f69-b6f6-dcaedfdc4bb7_reliable</a:To>
            </s:Header>
            <s:Body>
                <RelayedConnect xmlns="http://schemas.microsoft.com/netservices/2009/05/servicebus/relayedconnect">
                    <Id>39aadc47-3295-4a41-a886-51ad9e0cca37</Id>
                    <IpAddress>2748520724</IpAddress>
                    <IpPort>9352</IpPort>
                    <HttpAddress>2748520724</HttpAddress>
                    <HttpPort>80</HttpPort>
                    <HttpsAddress>2748520724</HttpsAddress>
                    <HttpsPort>443</HttpsPort>
                    <InstanceDnsAddress>g17-prod-ch3-006-sb.servicebus.windows.net</InstanceDnsAddress>
                </RelayedConnect>
            </s:Body>
        </s:Envelope>
        """
        relayed_connect = relayed_xml_root.find('.//sb:RelayedConnect', namespaces)
        if relayed_connect is not None:
            for param in relayed_connect:
                key = param.tag.split('}')[-1]
                value = param.text
                msg.add(key, value)

    elif message_type == "RelayedAcceptReply":
        """
        <s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" xmlns:a="http://www.w3.org/2005/08/addressing">
            <s:Header>
                <a:Action s:mustUnderstand="1">RelayedAcceptReply</a:Action>
            </s:Header>
            <s:Body>
                <z:anyType xmlns:z="http://schemas.microsoft.com/2003/10/Serialization/" xmlns:i="http://www.w3.org/2001/XMLSchema-instance"/>
            </s:Body>
        </s:Envelope>
        """
        pass  # As defined in the XML snippet

    elif message_type == "http://schemas.xmlsoap.org/ws/2005/02/rm/CreateSequence":
        """
        <s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" xmlns:a="http://www.w3.org/2005/08/addressing">
            <s:Header>
                <a:Action s:mustUnderstand="1">http://schemas.xmlsoap.org/ws/2005/02/rm/CreateSequence</a:Action>
                <a:MessageID>urn:uuid:7c4071d7-4bb0-4993-ae33-4d94ac4f844d</a:MessageID>
                <a:To s:mustUnderstand="1">sb://his-nam1-wus2.servicebus.windows.net/[redacted]_17d93d40-1389-4f69-b6f6-dcaedfdc4bb7_reliable</a:To>
            </s:Header>
            <s:Body>
                <CreateSequence xmlns="http://schemas.xmlsoap.org/ws/2005/02/rm">
                    <AcksTo>
                        <a:Address>http://www.w3.org/2005/08/addressing/anonymous</a:Address>
                    </AcksTo>
                    <Offer>
                        <Identifier>urn:uuid:da98a5eb-4130-427d-a1a3-09fe238623b4</Identifier>
                    </Offer>
                </CreateSequence>
            </s:Body>
        </s:Envelope>
        """
        msg["Type"] = "CreateSequence"
        try:
            identifier = xml_root.find('.//Identifier', namespaces).text
            msg.add("Identifier", identifier)
        except ET.ParseError:
            pass

    elif message_type == "http://tempuri.org/IConnectorSignalingService/SignalConnector":
        # Check TrafficProtocol within the body
        try:
            traffic_protocol = xml_root.find('.//TrafficProtocol', namespaces).text
            if traffic_protocol == "Connect":
                """
                <s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" xmlns:r="http://schemas.xmlsoap.org/ws/2005/02/rm" xmlns:a="http://www.w3.org/2005/08/addressing">
                    <s:Header>
                        <r:AckRequested>
                            <r:Identifier>urn:uuid:00000000-0000-0000-0000-000000000000</r:Identifier>
                        </r:AckRequested>
                        <r:Sequence s:mustUnderstand="1">
                            <r:Identifier>urn:uuid:00000000-0000-0000-0000-000000000000</r:Identifier>
                            <r:MessageNumber>1</r:MessageNumber>
                        </r:Sequence>
                        <a:Action s:mustUnderstand="1">http://tempuri.org/IConnectorSignalingService/SignalConnector</a:Action>
                        <a:MessageID>urn:uuid:23f43182-7b11-4bbf-981a-8d0fc078b8c1</a:MessageID>
                        <a:ReplyTo>
                            <a:Address>http://www.w3.org/2005/08/addressing/anonymous</a:Address>
                        </a:ReplyTo>
                        <a:To s:mustUnderstand="1">sb://his-nam1-wus2.servicebus.windows.net/[redacted]_17d93d40-1389-4f69-b6f6-dcaedfdc4bb7_reliable</a:To>
                    </s:Header>
                    <s:Body>
                        <SignalConnector xmlns="http://tempuri.org/">
                            <messageProperties xmlns:b="http://schemas.datacontract.org/2004/07/Microsoft.ApplicationProxy.Common.SignalingDataModel" xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
                                <RequestId xmlns="http://schemas.datacontract.org/2004/07/Microsoft.ApplicationProxy.Common.RequestContexts">2f2ab3af-5e56-45a7-865e-bb3243f06d00</RequestId>
                                <SessionId xmlns="http://schemas.datacontract.org/2004/07/Microsoft.ApplicationProxy.Common.RequestContexts">00000000-0000-0000-0000-000000000000</SessionId>
                                <SubscriptionId xmlns="http://schemas.datacontract.org/2004/07/Microsoft.ApplicationProxy.Common.RequestContexts">[redacted]</SubscriptionId>
                                <TransactionId xmlns="http://schemas.datacontract.org/2004/07/Microsoft.ApplicationProxy.Common.RequestContexts">9c3f0681-e562-4d1d-8f4c-9ef5357ba040</TransactionId>
                                <b:OverrideServiceHostEnabled>true</b:OverrideServiceHostEnabled>
                                <b:OverridenReturnHost>vm7-proxy-pta-WUS-SJC01P-3.connector.his.msappproxy.net</b:OverridenReturnHost>
                                <b:OverridenReturnPort>443</b:OverridenReturnPort>
                                <b:ReturnHost>vm7-proxy-pta-WUS-SJC01P-3.connector.his.msappproxy.net</b:ReturnHost>
                                <b:ReturnPort>10100</b:ReturnPort>
                                <b:TunnelContext>
                                    <ConfigurationHash xmlns="">-139793387</ConfigurationHash>
                                    <CorrelationId xmlns="">9c3f0681-e562-4d1d-8f4c-9ef5357ba040</CorrelationId>
                                    <HasPayload xmlns="">false</HasPayload>
                                    <ProtocolContext i:type="ConnectContext" xmlns="">
                                        <TrafficProtocol>Connect</TrafficProtocol>
                                        <ConnectionId>8457828f-e336-44bf-b967-4044b1478cc1</ConnectionId>
                                    </ProtocolContext>
                                </b:TunnelContext>
                            </messageProperties>
                        </SignalConnector>
                    </s:Body>
                </s:Envelope>
                """
                msg["Type"] = "SignalConnector"
                msg.add("RequeIdentifierstId", xml_root.find('.//r:Identifier', namespaces).text)
                msg.add("MessageNumber", xml_root.find('.//r:MessageNumber', namespaces).text)
                msg.add("RequestId", xml_root.find('.//RequestId', namespaces).text)
                msg.add("SessionId", xml_root.find('.//SessionId', namespaces).text)
                msg.add("SubscriptionId", xml_root.find('.//SubscriptionId', namespaces).text)
                msg.add("TransactionId", xml_root.find('.//TransactionId', namespaces).text)
                msg.add("ConnectionId", xml_root.find('.//ConnectionId', namespaces).text)
                msg.add("ReturnHost", xml_root.find('.//b:ReturnHost', namespaces).text)
                msg.add("ReturnPort", xml_root.find('.//b:ReturnPort', namespaces).text)

            elif traffic_protocol == "PasswordValidation":
                """
                <s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" xmlns:a="http://www.w3.org/2005/08/addressing">
                    <s:Header>
                        <a:Action s:mustUnderstand="1">http://tempuri.org/IConnectorSignalingService/SignalConnector</a:Action>
                        <a:MessageID>urn:uuid:5a445862-847b-44f6-a076-3a42ba286999</a:MessageID>
                        <a:ReplyTo>
                            <a:Address>http://www.w3.org/2005/08/addressing/anonymous</a:Address>
                        </a:ReplyTo>
                        <a:To s:mustUnderstand="1">sb://his-nam1-wus2.servicebus.windows.net/[redacted]_17d93d40-1389-4f69-b6f6-dcaedfdc4bb7</a:To>
                    </s:Header>
                    <s:Body>
                        <SignalConnector xmlns="http://tempuri.org/">
                            <messageProperties xmlns:b="http://schemas.datacontract.org/2004/07/Microsoft.ApplicationProxy.Common.SignalingDataModel" xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
                                <RequestId xmlns="http://schemas.datacontract.org/2004/07/Microsoft.ApplicationProxy.Common.RequestContexts">dff0f331-bb52-4cd0-9b6f-b741343d6d00</RequestId>
                                <SessionId xmlns="http://schemas.datacontract.org/2004/07/Microsoft.ApplicationProxy.Common.RequestContexts">00000000-0000-0000-0000-000000000000</SessionId>
                                <SubscriptionId xmlns="http://schemas.datacontract.org/2004/07/Microsoft.ApplicationProxy.Common.RequestContexts">[redacted]</SubscriptionId>
                                <TransactionId xmlns="http://schemas.datacontract.org/2004/07/Microsoft.ApplicationProxy.Common.RequestContexts">41bf611b-36d5-42d3-9151-2be2477279f4</TransactionId>
                                <b:OverrideServiceHostEnabled>true</b:OverrideServiceHostEnabled>
                                <b:OverridenReturnHost>vm4-proxy-pta-WUS-SJC01P-3.connector.his.msappproxy.net</b:OverridenReturnHost>
                                <b:OverridenReturnPort>443</b:OverridenReturnPort>
                                <b:ReturnHost>vm4-proxy-pta-WUS-SJC01P-3.connector.his.msappproxy.net</b:ReturnHost>
                                <b:ReturnPort>10100</b:ReturnPort>
                                <b:TunnelContext>
                                    <ConfigurationHash xmlns="">-139793387</ConfigurationHash>
                                    <CorrelationId xmlns="">41bf611b-36d5-42d3-9151-2be2477279f4</CorrelationId>
                                    <HasPayload xmlns="">false</HasPayload>
                                    <ProtocolContext i:type="PasswordValidationContext" xmlns="">
                                        <TrafficProtocol>PasswordValidation</TrafficProtocol>
                                        <Domain>AADSECURITY</Domain>
                                        <EncryptedData>
                                            <b:EncryptedOnPremValidationData>
                                                            <b:Base64EncryptedData>qopI[redacted]K4NFs8fgmzNaA0XL41w==</b:Base64EncryptedData>
                                                            <b:KeyIdentifer>[redacted]_44C483C48946CF3BAC85D22018EB134FB4B6460D</b:KeyIdentifer>
                                            </b:EncryptedOnPremValidationData>
                                            <b:EncryptedOnPremValidationData>
                                                            <b:Base64EncryptedData>QZdwL[redacted]nP94w4/meAYX0w==</b:Base64EncryptedData>
                                                            <b:KeyIdentifer>[redacted]_0CAF09C29EFA51DAFA91528949B253F977ED763D</b:KeyIdentifer>
                                            </b:EncryptedOnPremValidationData>
                                            <b:EncryptedOnPremValidationData>
                                                            <b:Base64EncryptedData>flQwZQ[redacted]EtAetg==</b:Base64EncryptedData>
                                                            <b:KeyIdentifer>[redacted]_893657AEAE25D4C913BCF37CB138628772BE1B52</b:KeyIdentifer>
                                            </b:EncryptedOnPremValidationData>
                                        </EncryptedData>
                                        <Password/>
                                        <UserPrincipalName>AllanD@[redacted]</UserPrincipalName>
                                    </ProtocolContext>
                                </b:TunnelContext>
                            </messageProperties>
                        </SignalConnector>
                    </s:Body>
                </s:Envelope>
                """
                msg["Type"] = "PasswordValidation"
                msg.add("RequestId", xml_root.find('.//RequestId', namespaces).text)
                msg.add("SessionId", xml_root.find('.//SessionId', namespaces).text)
                msg.add("SubscriptionId", xml_root.find('.//SubscriptionId', namespaces).text)
                msg.add("TransactionId", xml_root.find('.//TransactionId', namespaces).text)
                msg.add("CorrelationId", xml_root.find('.//CorrelationId', namespaces).text)
                msg.add("ReturnHost", xml_root.find('.//b:ReturnHost', namespaces).text)
                msg.add("ReturnPort", xml_root.find('.//b:ReturnPort', namespaces).text)
                msg.add("UserPrincipalName", xml_root.find('.//UserPrincipalName', namespaces).text)

                encdata = xml_root.findall('.//b:Base64EncryptedData', namespaces)
                identifiers = xml_root.findall('.//b:KeyIdentifer', namespaces)
                encryptedData = []
                for i in range(len(encdata)):
                    encryptedData.append({
                        "Base64EncryptedData": encdata[i],
                        "KeyIdentifer": identifiers[i]
                    })
                msg.add("EncryptedData", encryptedData)


        except AttributeError:
            pass

    elif message_type == "http://www.w3.org/2005/08/addressing/soap/fault":
        """
        <s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" xmlns:a="http://www.w3.org/2005/08/addressing">
            <s:Header>
                <a:Action s:mustUnderstand="1">http://www.w3.org/2005/08/addressing/soap/fault</a:Action>
                <a:To s:mustUnderstand="1">sb://his-nam1-ncus1.servicebus.windows.net/[redacted]_17d93d40-1389-4f69-b6f6-dcaedfdc4bb7_reliable</a:To>
            </s:Header>
            <s:Body>
                <s:Fault>
                    <s:Code>
                        <s:Value>s:Sender</s:Value>
                        <s:Subcode>
                            <s:Value xmlns:a="http://schemas.xmlsoap.org/ws/2005/02/rm">a:UnknownSequence</s:Value>
                        </s:Subcode>
                    </s:Code>
                    <s:Reason>
                        <s:Text xml:lang="en-US">The value of wsrm:Identifier is not a known Sequence identifier.</s:Text>
                    </s:Reason>
                    <s:Detail>
                        <r:Identifier xmlns:r="http://schemas.xmlsoap.org/ws/2005/02/rm">urn:uuid:4213aeec-4fa2-459e-89d4-5fa8e58cf1bb</r:Identifier>
                    </s:Detail>
                </s:Fault>
            </s:Body>
        </s:Envelope>
        """
        msg["Type"] = "Fault"
        try:
            value = xml_root.find('.//s:Value', namespaces).text
            reason = xml_root.find('.//s:Text', namespaces).text
            msg.add("Value", value)
            msg.add("Reason", reason)
        except AttributeError:
            pass

    elif message_type == "http://schemas.xmlsoap.org/ws/2005/02/rm/AckRequested":
        """
        <s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" xmlns:r="http://schemas.xmlsoap.org/ws/2005/02/rm" xmlns:a="http://www.w3.org/2005/08/addressing">
            <s:Header>
                <r:AckRequested>
                    <r:Identifier>urn:uuid:bcb65644-d0f1-4a11-adaf-ff844eb5f4ea</r:Identifier>
                </r:AckRequested>
                <a:Action s:mustUnderstand="1">http://schemas.xmlsoap.org/ws/2005/02/rm/AckRequested</a:Action>
                <a:To s:mustUnderstand="1">sb://his-nam1-wus2.servicebus.windows.net/[redacted]_17d93d40-1389-4f69-b6f6-dcaedfdc4bb7_reliable</a:To>
            </s:Header>
            <s:Body/>
        </s:Envelope>
        """
        msg["Type"] = "AckRequested"
        try:
            identifier = xml_root.find('.//r:Identifier', namespaces).text
            to = xml_root.find('.//a:To', namespaces).text
            msg.add("Identifier", identifier)
            msg.add("To", to)
        except AttributeError:
            pass

    return msg


# def parse_relay_message(message_bytes: bytes) -> Union[None, ParsedMessage]:
#     if message_bytes and len(message_bytes) > 3:
#         msg_type = message_bytes[0]
#         if msg_type == 0x56:
#             return parse_relay_binary_xml(message_bytes, 0, True)
#         elif msg_type == 0x06:
#             pos = 1
#             size = parse_multi_byte_int31(message_bytes, pos)
#             return parse_relay_binary_xml(message_bytes, pos)
#         elif msg_type in [0x07, 0xAA, 0x98, 0x00]:
#             message = ParsedMessage(message_bytes)
#             if msg_type == 0x07:
#                 message.add("Type", "Disconnect")
#             elif msg_type == 0xAA:
#                 message.add("Type", "RelayResponseError")
#             elif msg_type == 0x98:
#                 message.add("Type", "RelayResponseOk")
#             elif msg_type == 0x00:
#                 message.add("Type", "RelaySB")
#                 sb_size = message_bytes[6]
#                 sb_string = message_bytes[7:7+sb_size].decode('utf-8')
#                 message.add("SB", sb_string)
#             return message
#     return None
