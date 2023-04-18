import config
import datetime
import logging
from pyzabbix import ZabbixAPI

logging.basicConfig(level=config.LOGGING_LEVEL)

RESOLVED_PROBLEMS = True
UNRESOLVED_PROBLEMS_ONLY = False
RECENT_PROBLEMS = UNRESOLVED_PROBLEMS_ONLY
PROBLEMS_OUTPUT_FIELDS_DICT = [
    'eventid',
    'clock',
    'name',
    'severity',
]
NAME_FIELD = 'name'
HOST_ID_FIELD = 'hostid'
HOST_FIELD = 'host'
API_INFO_VERSION = 'apiinfo.version'

CLOCK_FIELD = 'clock'
SEVERITY_FIELD = 'severity'
TIME_TEMPLATE = '%Y-%m-%d %H:%M:%S'
PROBLEMS_TIME_DAYS_RANGE = 30

SEVERITY_CLASSIFIED = 0
SEVERITY_INFORMATION = 1
SEVERITY_WARNING = 2
SEVERITY_AVERAGE = 3
SEVERITY_HIGH = 4
SEVERITY_DISASTER = 5
SEVERITIES = [SEVERITY_DISASTER, SEVERITY_HIGH, SEVERITY_AVERAGE, SEVERITY_WARNING]

ITEMS_LAST_VALUE = 'lastvalue'
SORT_FIELD_KEY = 'key_'
SORT_FIELD_NAME = 'name'


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

    def get_all_items(self, host_ids: list):
        return self._zabbix_api.item.get(hostids=host_ids)

    def get_item_by_key(self, host_ids: list, item_name: str):
        return self._zabbix_api.item.get(
            hostids=host_ids,
            search={SORT_FIELD_KEY: item_name},
            output=[ITEMS_LAST_VALUE],
        )

    def get_item_by_name(self, host_ids: list, item_name: str):
        return self._zabbix_api.item.get(
            hostids=host_ids,
            search={SORT_FIELD_NAME: item_name},
            output=[ITEMS_LAST_VALUE],
        )

    def get_all_monitored_hosts(self) -> list:
        return self._zabbix_api.host.get(status=1, monitored_hosts=1, selectInterfaces=['ip'])

    def get_monitored_hosts(self, host_ids: list) -> list:
        return self._zabbix_api.host.get(
            output=[
                'hostid',
                'host',
                'name',
                'snmp_error',
                'error',
            ],
            hostids=host_ids,
            status=1,
            monitored_hosts=1,
            selectInterfaces=['ip'],
        )

    def get_host_problem(self, host_id, time_from: int = None) -> list:
        if time_from:
            return self._zabbix_api.problem.get(
                hostids=host_id,
                recent=RECENT_PROBLEMS,
                severities=SEVERITIES,
                time_from=time_from,
                output=PROBLEMS_OUTPUT_FIELDS_DICT,
            )
        else:
            return self._zabbix_api.problem.get(
                hostids=host_id,
                recent=RECENT_PROBLEMS,
                severities=SEVERITIES,
                output=PROBLEMS_OUTPUT_FIELDS_DICT,
            )


def get_time_from_now(days_offset=PROBLEMS_TIME_DAYS_RANGE):
    delta_time = datetime.datetime.today() - datetime.timedelta(days=days_offset)
    logging.debug(f'Get delta: ({days_offset}) days -  Date: {delta_time} from now')
    return int(delta_time.timestamp())


def get_zabbix_monitoring_hosts(host_ids: list) -> list:
    with ZabbixMonitoring() as zabbix_monitoring:
        hosts = zabbix_monitoring.get_monitored_hosts(host_ids)
    return hosts


def get_all_host_items(host_ids: list) -> list:
    with ZabbixMonitoring() as zabbix_monitoring:
        items = zabbix_monitoring.get_all_items(host_ids)
    return items


def get_host_item_value(host_ids: list, item_name: str) -> str:
    result = ''
    host_ids = [host_ids]
    with ZabbixMonitoring() as zabbix_monitoring:
        items = zabbix_monitoring.get_item_by_key(host_ids, item_name)
        if items:
            try:
                value = int(float(items[0][ITEMS_LAST_VALUE]))
                result = str(value)
            except (IndexError, KeyError) as err:
                logging.error(f'{err}')
                result = ''
    return result


def get_all_zabbix_monitoring_hosts() -> list:
    with ZabbixMonitoring() as zabbix_monitoring:
        hosts = zabbix_monitoring.get_all_monitored_hosts()
    return hosts


def get_zabbix_host_problems(host_id: int, with_time_from: bool = False) -> list:
    result = []
    with ZabbixMonitoring() as zabbix_monitoring:
        try:
            if with_time_from:
                time_from = get_time_from_now()
                host_problems = list(zabbix_monitoring.get_host_problem(host_id, time_from))
            else:
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
        # Сортировка должна быть по SEVERITY_FIELD и reverse=True чтобы получить корректный цвет ошибки на карточке
        result = sorted(result, reverse=True, key=lambda x: x[SEVERITY_FIELD])
    return result


def main():
    # hosts = get_zabbix_monitoring_hosts([10451, 10434])
    print(get_host_item_value([10436], 'ups.temperature'))

    # hosts = get_all_zabbix_monitoring_hosts()
    # for host in hosts:
    #     interface = host['interfaces'][0]['ip']
    #     logging.info('--------------------------------------------------------\r\n'
    #                  'Host: "{host}", Hostid: "{hostid}" Name: "{name}"\r\nInterface: {interfaces}\r\n'.format(
    #         host=host[HOST_FIELD],
    #         hostid=host[HOST_ID_FIELD],
    #         name=host['name'],
    #         interfaces=interface,
    #     ))
    #     # problems = get_zabbix_host_problems(host[HOST_ID_FIELD], with_time=True)
    #     problems = get_zabbix_host_problems(host[HOST_ID_FIELD])
    #     for problem in problems:
    #         logging.info('Problem: {eventid}, clock: {clock} name: {name} Severity: {severity}\r\n'.format(
    #             eventid=problem['eventid'],
    #             clock=problem['clock'],
    #             name=problem['name'],
    #             severity=problem['severity'],
    #         ))
    return


if __name__ == '__main__':
    main()
