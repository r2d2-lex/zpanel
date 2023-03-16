import config
import logging
from datetime import datetime
from pyzabbix import ZabbixAPI
from schema import Host, Problem

logging.basicConfig(level=config.LOGGING_LEVEL)

UNRESOLVED_PROBLEMS_ONLY = False


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
        answer = self._zabbix_api.do_request('apiinfo.version')
        print('Zabbix Api Version: {}'.format(answer['result']))

    def __str__(self):
        return 'ZabbixMonitoring'

    def get_all_hosts(self) -> list:
        all_hosts = self._zabbix_api.host.get(status=1)
        result = []

        for list_item in all_hosts:
            try:
                host = Host(
                    hostid=list_item['hostid'],
                    host=list_item['host'],
                    name=list_item['name'],
                    error=list_item['error'],
                    snmp_error=list_item['snmp_error'],
                )
            except (IndexError, KeyError) as err:
                logging.error(f'type {type(err)}')
                continue

            result.append(host)
            logging.info('Host: "{}" Name: "{}"\r\nErrors: "{}" snmp_error: "{}"\r\n'.format(
                    host.host,
                    host.name,
                    host.error,
                    host.snmp_error,
                )
            )

        return result

    def get_host_problem(self, hostname, host_id) -> list:
        result = []
        logging.info(f'Problems for "{hostname}":')
        problems = self._zabbix_api.problem.get(hostids=host_id, recent=UNRESOLVED_PROBLEMS_ONLY)
        for problem_item in problems:
            try:
                clock = datetime.utcfromtimestamp(int(problem_item['clock'])).strftime('%Y-%m-%d %H:%M:%S')
                problem = Problem(
                    hostid=host_id,
                    name=problem_item['name'],
                    eventid=problem_item['eventid'],
                    clock=str(clock),
                    severity=problem_item['severity'],
                )
            except (IndexError, KeyError)as err:
                logging.error(f'type {type(err)}')
                continue

            result.append(problem)

            logging.info(
                '{} - {} - {} - {} - {}'.format(
                    problem.hostid,
                    problem.eventid,
                    problem.severity,
                    problem.clock,
                    problem.name,
                )
            )
        print('\r\n')
        return result


def main():
    with ZabbixMonitoring() as zabbix_monitoring:
        hosts = zabbix_monitoring.get_all_hosts()
        for host in hosts:
            if host.error or host.snmp_error:
                zabbix_monitoring.get_host_problem(host.host, host.hostid)


if __name__ == '__main__':
    main()
