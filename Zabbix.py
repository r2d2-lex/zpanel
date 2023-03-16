import config
import logging
from pyzabbix import ZabbixAPI

logging.basicConfig(level=config.LOGGING_LEVEL)


class ZabbixMonitoring:
    zabbix_api = ZabbixAPI(config.ZABBIX_API_URL, user=config.ZABBIX_API_USER, password=config.ZABBIX_API_PASSWORD)

    def __init__(self):
        self._zabbix_api = self.zabbix_api
        self._all_hosts = ''

    def __repr__(self):
        answer = self._zabbix_api.do_request('apiinfo.version')
        print('Zabbix Api Version: {}'.format(answer['result']))

    def __str__(self):
        return 'ZabbixAPI'

    def get_all_hosts(self):
        self._all_hosts = self._zabbix_api.host.get(status=1)
        result = ''

        for list_item in self._all_hosts:
            try:
                result += 'Host: "{}" Name: "{}"\r\nErrors: "{}" snmp_error: "{}"\r\n\r\n'.format(
                        list_item['host'],
                        list_item['name'],
                        list_item['error'],
                        list_item['snmp_error'],
                    )
            except (IndexError, KeyError):
                pass

        return result


def main():
    zbx = ZabbixMonitoring()
    print(zbx.get_all_hosts())


if __name__ == '__main__':
    main()
