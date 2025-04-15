import io
from struct import pack
from xml_parser import XmlParser

# packet = bytes.fromhex('56020b0173040b0161065608440a1e0082990d52656c61796564416363657074440c1e00829946687474703a2f2f736368656d61732e6d6963726f736f66742e636f6d2f323030352f31322f536572766963654d6f64656c2f41646472657373696e672f416e6f6e796d6f757301560e400d52656c617965644163636570740843687474703a2f2f736368656d61732e6d6963726f736f66742e636f6d2f6e657473657276696365732f323030392f30352f736572766963656275732f636f6e6e65637409016929687474703a2f2f7777772e77332e6f72672f323030312f584d4c536368656d612d696e7374616e636540024964992461376438373462352d666665302d343463362d616137632d646639636331303036336336010101')

# packet = bytes.fromhex('56020B0173040B0161065608440A1E0082AB9A05441AADAAB5E828CF5FE344A7F823F9D6B74B69440C1E0082998A73623A2F2F6869732D73622D68697367656E6572616C2D6575722D77657572312E736572766963656275732E77696E646F77732E6E65742F65343638363665392D346230302D343534342D626265362D3564656463663365326663665F34643864373136372D333863332D343461312D383264302D3830666162313336303463385F72656C6961626C6501560E4298050A20429405442AAB140142B205421EAD55AB784A6816DF4A9681CD6894FF588F01010101')

# packet = bytes.fromhex('06e3010056020b0173040b0161065608440a1e0082ab9a05441aad2a9c2ee875ae6f4281135d77d964a74d440c1e0082998a73623a2f2f6869732d73622d68697367656e6572616c2d6575722d6e657572312e736572766963656275732e77696e646f77732e6e65742f65343638363665392d346230302d343534342d626265362d3564656463663365326663665f34643864373136372d333863332d343461312d383264302d3830666162313336303463385f72656c6961626c6501560e4298050a20429405442aab140142b205421ead1ccbb04b32495d4782640809dab6df8a01010101')

# packet = bytes.fromhex('06e3010056020b0173040b0161065608440a1e0082ab9a05441aad6c55fb1ea9073a4ca6d917abbea413ac440c1e0082998a73623a2f2f6869732d73622d68697367656e6572616c2d6575722d6e657572312e736572766963656275732e77696e646f77732e6e65742f65343638363665392d346230302d343534342d626265362d3564656463663365326663665f34643864373136372d333863332d343461312d383264302d3830666162313336303463385f72656c6961626c6501560e4298050a20429405442aab140142b205421eadc80df3b9ef2a6846bfbe813edfd9579d01010101')

# xml_string = XmlParser(packet).unserialize()
# print(xml_string)

# import xml.etree.ElementTree as ET
# xml_root = ET.fromstring(xml_string)
# namespaces = {
#     'a': "http://www.w3.org/2005/08/addressing",
#     'b': "http://schemas.datacontract.org/2004/07/Microsoft.ApplicationProxy.Common.SignalingDataModel",
#     'netrm': "http://schemas.microsoft.com/ws/2006/05/rm",
#     'i': "http://www.w3.org/2001/XMLSchema-instance",
#     'r': "http://schemas.xmlsoap.org/ws/2005/02/rm",
#     's': "http://www.w3.org/2003/05/soap-envelope",
#     'sb': "http://schemas.microsoft.com/netservices/2009/05/servicebus/relayedconnect",
#     'wsrm': 'http://schemas.xmlsoap.org/ws/2005/02/rm'

# }

# identifier = xml_root.find('.//wsrm:Identifier', namespaces)
# print(identifier.text)

