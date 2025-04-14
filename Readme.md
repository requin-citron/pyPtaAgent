# pyPtaAgent

## Usage

```bash
$ python3 pyPTaAgent.py -c cert.pem -k key.pem -d azuretest.fr
```

## Setup

### Locally
```bash
$ python3 -m pip install -r requirements.txt
```

### Docker
```bash
$ docker build -t pyptaagent .
$ docker run pyptaagent --help
  
$ docker run -v /host/path/containing/certificates/:/app/shared pyptaagent -c ./shared/cert.pem -k ./shared/key.pem -d example.com
```

## Help
```bash
$ python3 pyPTaAgent.py --help
usage: pyPTaAgent.py [-h] -c CERT -k KEY (-t TENANTID | -d DOMAIN) [-v]

PTA Agent - Azure Service Bus Connector

options:
  -h, --help            show this help message and exit
  -t, --tenantid TENANTID
                        Azure tenant ID (default: None)
  -d, --domain DOMAIN   Domain name to look up tenant ID (default: None)
  -v, --verbose         Enable verbose output (DEBUG level) (default: False)

required arguments:
  -c, --cert CERT       Path to the certificate file (.pem) (default: None)
  -k, --key KEY         Path to the private key file (.pem) (default: None)
```