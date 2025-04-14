import asyncio, requests
import xml.etree.ElementTree as ET

from servicebus_client import ServiceBusWebSocketClient
from logger import logger

xml_bootstrap = """
<BootstrapRequest xmlns="http://schemas.datacontract.org/2004/07/Microsoft.ApplicationProxy.Common.SignalerDataModel" xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
<AgentSdkVersion>1.5.1542.0</AgentSdkVersion>
<AgentVersion>1.5.1542.0</AgentVersion>
<BootstrapAddOnRequests i:nil="true"/>
<BootstrapDataModelVersion>1.5.1542.0</BootstrapDataModelVersion>
<ConnectorId>{ConnectorId}</ConnectorId>
<ConnectorVersion i:nil="true"/>
<ConsecutiveFailures>0</ConsecutiveFailures>
<CurrentProxyPortResponseMode>Primary</CurrentProxyPortResponseMode>
<FailedRequestMetrics xmlns:a="http://schemas.datacontract.org/2004/07/Microsoft.ApplicationProxy.Common.BootstrapDataModel"/>
<InitialBootstrap>true</InitialBootstrap>
<IsProxyPortResponseFallbackDisabledFromRegistry>true</IsProxyPortResponseFallbackDisabledFromRegistry>
<LatestDotNetVersionInstalled>461814</LatestDotNetVersionInstalled>
<MachineName>{MachineName}</MachineName>
<OperatingSystemLanguage>1033</OperatingSystemLanguage>
<OperatingSystemLocale>040b</OperatingSystemLocale>
<OperatingSystemSKU>7</OperatingSystemSKU>
<OperatingSystemVersion>10.0.17763</OperatingSystemVersion>
<PerformanceMetrics xmlns:a="http://schemas.datacontract.org/2004/07/Microsoft.ApplicationProxy.Common.BootstrapDataModel">
<a:CpuAggregates/>
<a:CurrentActiveBackendWebSockets>0</a:CurrentActiveBackendWebSockets>
<a:FaultedServiceBusConnectionCount>0</a:FaultedServiceBusConnectionCount>
<a:FaultedWebSocketConnectionCount>0</a:FaultedWebSocketConnectionCount>
<a:LastBootstrapLatency>0</a:LastBootstrapLatency>
<a:TimeGenerated>2025-03-30T13:49:31.4249204Z</a:TimeGenerated>
</PerformanceMetrics>
<ProxyDataModelVersion>1.5.1542.0</ProxyDataModelVersion>
<RequestId>{RequestId}</RequestId>
<SubscriptionId>{SubscriptionId}</SubscriptionId>
<SuccessRequestMetrics xmlns:a="http://schemas.datacontract.org/2004/07/Microsoft.ApplicationProxy.Common.BootstrapDataModel"/>
<TriggerErrors/>
<UpdaterStatus>Stopped</UpdaterStatus>
<UseServiceBusTcpConnectivityMode>false</UseServiceBusTcpConnectivityMode>
<UseSpnegoAuthentication>false</UseSpnegoAuthentication>
</BootstrapRequest>
"""

class Settings:
    def __init__(self, access_key_name: str, access_key: str, namespace: str, service_path: str, cert_file: str, key_file: str) -> None:
        self.access_key_name = access_key_name
        self.access_key = access_key
        self.namespace = namespace
        self.service_path = service_path
        self.cert_file = cert_file
        self.key_file = key_file

class PTAAgent:
    def __init__(self, cert_file: str, keyfile: str, tenantid: str) -> None:
        self.cert_file = cert_file
        self.key_file = keyfile
        self.bootstrap = None
        self.tenantid = tenantid
        self.bootstrap = self.get_bootstrap()
        self.all_settings = self.parse_bootstrap()

    def get_bootstrap(self):
        logger.info("Querying bootstrap...")
        url = f'https://{self.tenantid}.pta.bootstrap.his.msappproxy.net/ConnectorBootstrap'
        response = requests.post(url, 
            cert=(self.cert_file, self.key_file), 
            data=xml_bootstrap.format(
                ConnectorId = "88cd5950-3d65-494c-996b-65e625ee294f",
                MachineName = "DC.company.com",
                RequestId = "0c891cd7-afae-49bd-8f40-2f52263c2c0a",
                SubscriptionId = "ae11aea0-4e67-438a-80a8-d877c5d4a885"
            ),
            headers={'Content-Type': 'application/xml'})
        root = ET.fromstring(response.text)
        return root

    def parse_bootstrap(self) -> None:
        ns = {
            'default': 'http://schemas.datacontract.org/2004/07/Microsoft.ApplicationProxy.Common.SignalerDataModel',
            'a': 'http://schemas.datacontract.org/2004/07/Microsoft.ApplicationProxy.Common.BootstrapDataModel',
        }
        all_settings = []
        logger.info("Parsing bootstrap...")
        endpoints = self.bootstrap.findall('.//a:SignalingListenerEndpointSettings', ns)
        for endpoint in endpoints:
            settings = Settings(
                access_key_name=endpoint.find('a:SharedAccessKeyName', ns).text,
                access_key=endpoint.find('a:SharedAccessKey', ns).text,
                namespace=endpoint.find('a:Namespace', ns).text,
                service_path=endpoint.find('a:ServicePath', ns).text,
                cert_file=self.cert_file,
                key_file=self.key_file
            )
            all_settings.append(settings)
        logger.info(f'{len(all_settings)} settings found')
        return all_settings
    
    async def run(self, idx: int = 0) -> None:
        if idx >= len(self.all_settings):
            logger.error(f"Invalid index: {idx}")
            return None
        logger.info(f'Starting listener on settings {idx}')
        settings = self.all_settings[idx]
        client = ServiceBusWebSocketClient(
            namespace=settings.namespace,
            cert_file=settings.cert_file,
            key_file=settings.key_file,
            shared_access_key_name=settings.access_key_name,
            shared_access_key=settings.access_key,
            service_path=settings.service_path,
            thread_id=idx
        )        
        await asyncio.gather(client.run(1))

    async def run_all(self) -> None:
        logger.info('Starting listeners on all settings')
        clients = []
        for idx, settings in enumerate(self.all_settings):
            client = ServiceBusWebSocketClient(
                namespace=settings.namespace,
                cert_file=settings.cert_file,
                key_file=settings.key_file,
                shared_access_key_name=settings.access_key_name,
                shared_access_key=settings.access_key,
                service_path=settings.service_path,
                thread_id=idx
            )
            clients.append(client)
        tasks = [client.run(thread_id) for thread_id, client in enumerate(clients)]
        await asyncio.gather(*tasks)