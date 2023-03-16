import config
import logging
import datetime
from pyzabbix import ZabbixAPI
from schema import Host, Problem

logging.basicConfig(level=config.LOGGING_LEVEL)


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
        self._all_hosts = self._zabbix_api.host.get(status=1)
        result = []

        for list_item in self._all_hosts:
            try:
                host = Host(
                    hostid=list_item['hostid'],
                    host=list_item['host'],
                    name=list_item['name'],
                    error=list_item['error'],
                    snmp_error=list_item['snmp_error'],
                )
                result.append(host)
                logging.info('Host: "{}" Name: "{}"\r\nErrors: "{}" snmp_error: "{}"'.format(
                        host.host,
                        host.name,
                        host.error,
                        host.snmp_error,
                    )
                )
                if host.error or host.snmp_error:
                    self.get_host_problem(host.host, host.hostid)
            except (IndexError, KeyError):
                pass

        return result

    def get_host_problem(self, hostname, host_id) -> list:
        result = []
        logging.info(f'Problems for "{hostname}":')
        problems = self._zabbix_api.problem.get(hostids=host_id, recent='false')
        for problem_item in problems:
            problem = Problem(
                hostid=host_id,
                name=problem_item['name'],
                eventid=problem_item['eventid'],
                clock=str(int(problem_item['clock'])),
                severity=problem_item['severity'],
            )
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
    with ZabbixMonitoring() as zbx:
        host = zbx.get_all_hosts()


if __name__ == '__main__':
    main()
