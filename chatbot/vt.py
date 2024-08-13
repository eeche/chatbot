import os
from splunklib.searchcommands import dispatch, GeneratingCommand, Option, Configuration
import virustotal3.core
import json

from dotenv import load_dotenv
# from config import virus_total_api_key as api_key

load_dotenv()

api_key = os.getenv('VIRUS_TOTAL_API_KEY')

def virustotal(query_item, query_type):
    """ virustotal api """
    result = {}
    if query_type == 'ip':
        virus_total = virustotal3.core.IP(api_key)
        result = virus_total.info_ip(query_item)
    elif query_type == 'domain':
        virus_total = virustotal3.core.Domians(api_key)
        result = virus_total.info_domain(query_item)
    elif query_type == 'url':
        virus_total = virustotal3.core.URL(api_key)
        result = virus_total.info_url(query_item)
    elif query_type == 'hash':
        virus_total = virustotal3.core.Files(api_key)
        result = virus_total.info_file(query_item)
    if 'data' in result and 'attributes' in result['data']:
        return result['data']['attributes']['last_analysis_stats']
    else:
        return result
    
# result = virustotal('1.1.1.1', 'ip')
# print()
