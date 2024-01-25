import requests
from ldap3 import Server, Connection, ALL, SUBTREE

# Zabbix API configuration
ZABBIX_API_URL = 'http://HOST:PORT/api_jsonrpc.php'
ZABBIX_AUTH_TOKEN = 'TOKEN'
ZABBIX_GROUP_NAME = 'Discovered hosts'
TEMPLATE_NAME = 'Windows by Zabbix agent'

# LDAP configuration
LDAP_SERVER = 'ldap://LDAP_HOST'
LDAP_USER = 'CN=USER,CN=Users,DC=domain,DC=local'
LDAP_PASSWORD = 'PASSWORD'
BASE_DN = 'CN=Computers,DC=domain,DC=local'

# Constants
AGENT_INTERFACE_TYPE = 1  # 1 for agent interface, adjust if needed
AGENT_PORT = '10050'  # Adjust the port if needed

# Configuration to ignore specific hosts
IGNORED_HOSTS = ['SERVER', 'SERVER2']

def api_request(api_url, auth_token, method, params=None):
    """
    Make a request to the Zabbix API.

    Parameters:
    - api_url (str): The URL of the Zabbix API.
    - auth_token (str): The Zabbix authentication token.
    - method (str): The Zabbix API method to call.
    - params (dict): Additional parameters for the API request.

    Returns:
    - dict: The JSON response from the API.

    Raises:
    - Exception: If the Zabbix API request fails.
    """
    request_data = {
        'jsonrpc': '2.0',
        'method': method,
        'params': params or {},
        'auth': auth_token,
        'id': 1
    }

    response = requests.post(api_url, json=request_data)
    result = response.json()

    if 'error' in result:
        raise Exception(f"Zabbix API error: {result['error']}")

    return result.get('result', {})

def get_template_id(api_url, auth_token, template_name):
    """
    Retrieve the ID of a Zabbix template by name.

    Parameters:
    - api_url (str): The URL of the Zabbix API.
    - auth_token (str): The Zabbix authentication token.
    - template_name (str): The name of the Zabbix template.

    Returns:
    - str: The Zabbix template ID.
    """
    filter_params = {'host': [template_name]}
    result = api_request(api_url, auth_token, 'template.get', {'filter': filter_params, 'output': 'extend'})

    if result:
        return result[0]['templateid']
    else:
        raise Exception(f"Failed to retrieve template ID for template '{template_name}' from Zabbix API.")

def get_group_id(api_url, auth_token, group_name):
    """
    Retrieve the ID of a Zabbix group by name.

    Parameters:
    - api_url (str): The URL of the Zabbix API.
    - auth_token (str): The Zabbix authentication token.
    - group_name (str): The name of the Zabbix group.

    Returns:
    - str: The Zabbix group ID.
    """
    filter_params = {'name': [group_name]}
    result = api_request(api_url, auth_token, 'hostgroup.get', {'filter': filter_params, 'output': 'extend'})

    if result:
        return result[0]['groupid']
    else:
        raise Exception(f"Failed to retrieve group ID for group '{group_name}' from Zabbix API.")

def get_hosts_from_zabbix(api_url, auth_token, group_id):
    """
    Retrieve a list of hosts from a specific Zabbix group.

    Parameters:
    - api_url (str): The URL of the Zabbix API.
    - auth_token (str): The Zabbix authentication token.
    - group_id (str): The Zabbix group ID.

    Returns:
    - list: List of dictionaries containing host information.
    """
    params = {'output': ['host', 'hostid'], 'selectInterfaces': ['ip'], 'groupids': group_id}
    result = api_request(api_url, auth_token, 'host.get', params)

    return result if result else []

def create_zabbix_host(api_url, auth_token, dns_name, group_id, template_name=TEMPLATE_NAME):
    """
    Create a host in Zabbix.

    Parameters:
    - api_url (str): The URL of the Zabbix API.
    - auth_token (str): The Zabbix authentication token.
    - dns_name (str): The DNS name of the host to be created.
    - group_id (str): The Zabbix group ID.
    - template_name (str): The name of the Zabbix template.

    Returns:
    - None

    Raises:
    - Exception: If the Zabbix API request fails.
    """
    template_id = get_template_id(api_url, auth_token, template_name)

    params = {
        'host': dns_name,
        'interfaces': [{'type': AGENT_INTERFACE_TYPE, 'main': 1, 'useip': 0, 'ip': '', 'dns': dns_name, 'port': AGENT_PORT}],
        'groups': [{'groupid': group_id}],
        'templates': [{'templateid': template_id}]
    }

    api_request(api_url, auth_token, 'host.create', params)

    print(f"Host '{dns_name}' created successfully.")

def get_hosts_from_ldap(ldap_server, ldap_user, ldap_password, base_dn):
    """
    Retrieve a list of hosts from LDAP.

    Parameters:
    - ldap_server (str): The URL of the LDAP server.
    - ldap_user (str): The LDAP username for authentication.
    - ldap_password (str): The LDAP password for authentication.
    - base_dn (str): The base DN for LDAP search.

    Returns:
    - list: List of DNS hostnames.

    Raises:
    - Exception: If the LDAP connection or search fails.
    """
    search_filter = '(&(objectClass=computer))'
    attributes = ['dNSHostName']

    server = Server(ldap_server, get_info=ALL)
    conn = Connection(server, user=ldap_user, password=ldap_password)

    try:
        if not conn.bind():
            raise Exception(f"Failed to bind to LDAP server: {conn.result}")

        conn.search(search_base=base_dn, search_filter=search_filter, search_scope=SUBTREE, attributes=attributes)

        return [entry[attribute].value for entry in conn.entries for attribute in attributes if attribute in entry]

    finally:
        conn.unbind()

def remove_zabbix_host(api_url, auth_token, host_id):
    """
    Remove a host in Zabbix based on its host ID.

    Parameters:
    - api_url (str): The URL of the Zabbix API.
    - auth_token (str): The Zabbix authentication token.
    - host_id (str): The Zabbix host ID to be removed.

    Returns:
    - None

    Raises:
    - Exception: If the Zabbix API request fails.
    """
    params = [host_id]
    api_request(api_url, auth_token, 'host.delete', params)

    print(f"Host with ID {host_id} removed successfully.")

if __name__ == "__main__":
    try:
        GROUP_ID = get_group_id(ZABBIX_API_URL, ZABBIX_AUTH_TOKEN, ZABBIX_GROUP_NAME)

        HOST_LIST_ZABBIX = get_hosts_from_zabbix(ZABBIX_API_URL, ZABBIX_AUTH_TOKEN, GROUP_ID)
        HOST_LIST_LDAP = get_hosts_from_ldap(LDAP_SERVER, LDAP_USER, LDAP_PASSWORD, BASE_DN)

        # Filter out ignored hosts
        HOST_LIST_LDAP = [host for host in HOST_LIST_LDAP if host not in IGNORED_HOSTS]

        ADD_HOSTS_LIST = [value for value in HOST_LIST_LDAP if value not in {item['host'] for item in HOST_LIST_ZABBIX}]
        REMOVE_HOSTS_LIST = [item for item in HOST_LIST_ZABBIX if item['host'] not in HOST_LIST_LDAP]

        for dns_name in ADD_HOSTS_LIST:
            create_zabbix_host(ZABBIX_API_URL, ZABBIX_AUTH_TOKEN, dns_name, GROUP_ID)

        for host_item in REMOVE_HOSTS_LIST:
            remove_zabbix_host(ZABBIX_API_URL, ZABBIX_AUTH_TOKEN, host_item['hostid'])

    except Exception as e:
        print(f"Error: {e}")
