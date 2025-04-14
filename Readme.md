# pyPtaAgent

## Usage

```bash
python3 main.py -c cert.pem -k key.pem -d azuretest.fr
```

## Help
```bash
$ python3 main.py --help
usage: main.py [-h] -c CERT -k KEY (-t TENANTID | -d DOMAIN) [-v]

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