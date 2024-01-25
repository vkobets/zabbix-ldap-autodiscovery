Russian Warship:
[![Russian Warship Go Fuck Yourself](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/badges/RussianWarship.svg)](https://stand-with-ukraine.pp.ua)

# Zabbix LDAP Integration Script

## Overview

This Python script facilitates the integration between Zabbix and an LDAP server for managing hosts. It retrieves hosts from LDAP and synchronizes them with Zabbix, allowing for the creation and removal of hosts based on LDAP information.

## Requirements

- Python 3.x
- Required Python libraries: `requests`, `ldap3`

## Configuration

### Zabbix Configuration

1. Obtain Zabbix API URL and authentication token.
2. Specify Zabbix API URL and authentication token in the script.

### LDAP Configuration

1. Specify LDAP server details (server URL, username, password, base DN) in the script.

## Usage

1. Run the script in a Python environment.
2. The script will fetch hosts from LDAP and Zabbix, compare them, and synchronize Zabbix accordingly.
3. Hosts listed in LDAP but not in Zabbix will be created.
4. Hosts listed in Zabbix but not in LDAP will be removed.
5. Ignored hosts specified in the `IGNORED_HOSTS` list will be excluded from processing.

## Customization

- Adjust constants such as `AGENT_INTERFACE_TYPE` and `AGENT_PORT` to match your Zabbix configuration.
- Customize the `IGNORED_HOSTS` list to exclude specific hosts from synchronization.

## License

This script is provided under the [MIT License](LICENSE).

## Acknowledgments

- [Zabbix](https://www.zabbix.com/) - Monitoring solution
- [python-ldap3](https://github.com/cannatag/python-ldap3) - LDAP library for Python
- [Requests](https://docs.python-requests.org/en/latest/) - HTTP library for Python

## Disclaimer

This script is provided as-is, and the author takes no responsibility for any issues or damages caused by its use. It is recommended to review and test the script in a controlled environment before deploying it in a production system.
