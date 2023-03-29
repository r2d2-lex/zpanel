import config
import datetime
import logging
from pyzabbix import ZabbixAPI

logging.basicConfig(level=config.LOGGING_LEVEL)

UNRESOLVED_PROBLEMS_ONLY = False
NAME_FIELD = 'name'
HOST_ID_FIELD = 'hostid'
HOST_FIELD = 'host'
API_INFO_VERSION = 'apiinfo.version'

CLOCK_FIELD = 'clock'
SEVERITY_FIELD = 'severity'
TIME_TEMPLATE = '%Y-%m-%d %H:%M:%S'


class ZabbixMonitoring:

    def __init__(self):
        self._zabbix_api = None
        self._all_hosts = ''

    def __enter__(self):
        self._zabbix_api = ZabbixAPI(
            config.ZABBIX_API_URL,
            user=config.ZABBIX_API_USER,
            password=config.ZABBIX_API_PASSWORD
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._zabbix_api.user.logout()

    def __repr__(self):
        answer = self._zabbix_api.do_request(API_INFO_VERSION)
        print('Zabbix Api Version: {}'.format(answer['result']))

    def __str__(self):
        return 'ZabbixMonitoring'

    def get_all_monitored_hosts(self) -> list:
        return self._zabbix_api.host.get(status=1, monitored_hosts=1, selectInterfaces=['ip'])

    def get_host_problem(self, host_id) -> list:
        return self._zabbix_api.problem.get(hostids=host_id, recent=UNRESOLVED_PROBLEMS_ONLY)


def get_zabbix_monitoring_hosts() -> list:
    with ZabbixMonitoring() as zabbix_monitoring:
        hosts = zabbix_monitoring.get_all_monitored_hosts()
    return hosts


def get_zabbix_host_problems(host_id: int) -> list:
    result = []
    with ZabbixMonitoring() as zabbix_monitoring:
        try:
            host_problems = list(zabbix_monitoring.get_host_problem(host_id))

            for problem in host_problems:
                try:
                    clock = datetime.datetime.utcfromtimestamp(int(problem[CLOCK_FIELD])).strftime(TIME_TEMPLATE)
                    problem.update({CLOCK_FIELD: clock})
                    result.append(problem)
                except KeyError as error:
                    logging.error(f'KeyError: {error}')
                    continue

        except TypeError as error:
            logging.error(f'Error return host: {host_id} problems: {error}')
    if result:
        result = sorted(result, reverse=False, key=lambda x: x[CLOCK_FIELD])
    return result


def main():
    # hosts = get_zabbix_monitoring_hosts()
    # for host in hosts:
    #     interface = host['interfaces'][0]['ip']
    #     logging.info('Host: "{host}", Hostid: "{hostid}" Name: "{name}"\r\nInterface: {interfaces}\r\n'.format(
    #         host=host[HOST_FIELD],
    #         hostid=host[HOST_ID_FIELD],
    #         name=host['name'],
    #         interfaces=interface,
    #     ))
    problems = get_zabbix_host_problems(10451)
    for problem in problems:
        logging.info('Problem: {eventid}, clock: {clock} name: {name}\r\n'.format(
            eventid=problem['eventid'],
            clock=problem['clock'],
            name=problem['name'],
        ))
    return


if __name__ == '__main__':
    main()
