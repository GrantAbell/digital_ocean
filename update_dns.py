import os
import urllib.request
from pathlib import Path
from pydo import Client
from dotenv import load_dotenv

def update_ddns(client: Client = None, domain_name: str = None, record_name: str = None):
    """
    Updates DNS A record to use current external IP address.
    Currently only supports sub-domains.

    Paramters:
        :token - Digital Ocean API Client (use pydo.Client)
        :domain_name - Domain to target
        :name - DNS Name to target for DDNS

    """
    if client == None:
        raise Exception("An authenticated pydo.Client is required for 'client' argument.")
    if domain_name == None:
        raise Exception("Domain Name is required for 'domain_name' argument.")
    if record_name == None:
        raise Exception("DNS A Record Name is required for 'record_name' agument.")
    
    external_ip = urllib.request.urlopen('https://api.ipify.org').read().decode('utf8')
    record = [{'id': r['id'], 'ip': r['data']} for r in client.domains.list_records(domain_name=domain_name)['domain_records'] if r['name']==record_name]
    
    if len(record)<0:
        raise Exception("No record found with that domain name")
    elif len(record)>1:
        raise Exception("More than one record found (this shouldn't happen)")
    else:
        record = record[0]
        record_id = record['id']
        if record['ip'] == external_ip:
            print("no change needed")
            exit()
    req = {
    "name": record_name,
    "type": "A",
    "data": str(external_ip)
    }

    resp = client.domains.patch_record(domain_name="apiclobberer.com", body=req, domain_record_id=record_id)
    print(resp)

if __name__ == '__main__':
    env_loaded = load_dotenv('.env')
    if not env_loaded:
        raise Exception("Make sure a '.env' file exists locally and only has one 'KEY=VALUE' assignment per line.")
    token = os.getenv('DIGITALOCEAN_TOKEN')
    if token == None:
        raise Exception("No 'DIGITALOCEAN_TOKEN' key/value assignment found in .env file.")
    else:
        client = Client(token=token)

    domain_name = 'mydomain.com'
    record_name = 'my.sub.mydomain.com'
    update_ddns(client=client, domain_name=domain_name, record_name=record_name)
