import argparse, asyncio, logging
from pta_agent import PTAAgent
from logger import logger, update_level
from utils import tenantid_lookup

def setup_logging(verbose: bool = False):
    """Configure logging level based on verbose flag"""
    level = logging.DEBUG if verbose else logging.INFO
    update_level(level)
    logger.setLevel(level)
    logger.info(f"Logging level set to {logging.getLevelName(level)}")

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="PTA Agent - Azure Service Bus Connector",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Required 
    required = parser.add_argument_group('required arguments')
    required.add_argument('-c', '--cert', required=True,
                        help='Path to the certificate file (.pem)')
    required.add_argument('-k', '--key', required=True,
                        help='Path to the private key file (.pem)')
    
    # Either tenantid or domain must be provided
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-t', '--tenantid',
                      help='Azure tenant ID')
    group.add_argument('-d', '--domain',
                      help='Domain name to look up tenant ID')
    
    # Optional arguments
    parser.add_argument('-v', '--verbose', action='store_true',
                      help='Enable verbose output (DEBUG level)')
    
    return parser.parse_args()

def main():
    args = parse_args()
    setup_logging(args.verbose)
    
    tenantid = args.tenantid if args.tenantid else tenantid_lookup(args.domain)
    agent = PTAAgent(
        cert_file=args.cert,
        keyfile=args.key,
        tenantid=tenantid
    )
    asyncio.run(agent.run_all())


if __name__ == '__main__':
    main()