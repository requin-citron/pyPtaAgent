import requests
from utils.logger import logger

def tenantid_lookup(domain: str) -> str:
    try:
        r = requests.get(f"https://login.microsoftonline.com/{domain}/v2.0/.well-known/openid-configuration")
        data = r.json()
        if "error" in data.keys():
            logger.error(f"Invalid domain: {domain}")
            return None
        elif "token_endpoint" in data.keys():
            tenant_id = data["token_endpoint"].split("/")[3]
            return tenant_id
        return None
    except:
        pass