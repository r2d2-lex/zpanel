import config
import datetime
import json
import logging
from aiorequest import post_data

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


logging.basicConfig(level=config.LOGGING_LEVEL)


class AioZabbixApi:

    def __init__(self):
        self.zabbix_api_url = config.ZABBIX_API_URL + 'api_jsonrpc.php'
        self._zabbix_auth = None

    def __str__(self):
        return 'ZabbixMonitoring'

    async def __aenter__(self):
        await self.zabbix_login()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.zabbix_logout()

    async def _zabbix_request(self, method: str, params=None):
        result = ''
        request_json = {
            'jsonrpc': '2.0',
            'method': method,
            'params': params or {},
            'id': '1',
        }
        if self._zabbix_auth:
            request_json.update({'auth': self._zabbix_auth})
        logging.debug(f'Method {method} Request json {request_json}...')

        data = json.dumps(request_json)
        if not isinstance(data, bytes):
            data = data.encode("utf-8")

        result_data = await post_data(self.zabbix_api_url, data)

        try:
            result = result_data['result']
        except KeyError as error:
            logging.debug(f'Method: {method} error {error}...')
        return result

    async def zabbix_host_get(self, params):
        method = 'host.get'
        return await self._zabbix_request(method, params=params)

    async def zabbix_problem_get(self, params):
        method = 'problem.get'
        return await self._zabbix_request(method, params=params)

    async def zabbix_item_get(self, params):
        method = 'item.get'
        return await self._zabbix_request(method, params=params)

    async def get_item_by_key(self, host_ids: list, item_name: str):
        return await self.zabbix_item_get(dict(
            hostids=host_ids,
            search={SORT_FIELD_KEY: item_name},
            output=[ITEMS_LAST_VALUE],
        ))

    async def zabbix_login(self):
        method = 'user.login'
        params = {config.ZABBIX_API_USER_FIELD: config.ZABBIX_API_USER, 'password': config.ZABBIX_API_PASSWORD}
        self._zabbix_auth = await self._zabbix_request(method, params=params)
        return self._zabbix_auth

    async def zabbix_logout(self):
        method = 'user.logout'
        return await self._zabbix_request(method)

    async def get_host_item_value(self, host_ids: list, item_name: str) -> str:
        result = ''
        items = await self.get_item_by_key(host_ids, item_name)
        if items:
            try:
                value = int(float(items[0][ITEMS_LAST_VALUE]))
                result = str(value)
            except (IndexError, KeyError) as err:
                logging.error(f'{err}')
                result = ''
        return result

    async def get_host_problem(self, host_id) -> list:
        return await self.zabbix_problem_get(dict(
            hostids=host_id,
            recent=RECENT_PROBLEMS,
            severities=SEVERITIES,
            output=PROBLEMS_OUTPUT_FIELDS_DICT,
        )
        )

    async def get_monitored_hosts(self, host_ids: list) -> list:
        return await self.zabbix_host_get(dict(
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
        ))


async def get_zabbix_monitoring_hosts(host_ids: list) -> list:
    async with AioZabbixApi() as aio_zabbix:
        hosts = await aio_zabbix.get_monitored_hosts(host_ids)
    return hosts


async def get_all_zabbix_monitoring_hosts() -> list:
    async with AioZabbixApi() as aio_zabbix:
        params = dict(status=1, monitored_hosts=1, selectInterfaces=['ip'])
        hosts = await aio_zabbix.zabbix_host_get(params)
    return hosts


async def get_zabbix_host_problems(api, host_id: int) -> list:
    problem_list = []
    host_problems = await api.get_host_problem(host_id)
    for problem in host_problems:
        try:
            clock = datetime.datetime.fromtimestamp(int(problem[CLOCK_FIELD]))
            clock = clock.strftime(TIME_TEMPLATE)
            problem.update({CLOCK_FIELD: clock})
            problem_list.append(problem)
        except KeyError as error:
            logging.error(f'KeyError: {error}')
            continue
    if problem_list:
        # Сортировка должна быть по SEVERITY_FIELD и reverse=True чтобы получить корректный цвет ошибки на карточке
        problem_list = sorted(problem_list, reverse=True, key=lambda x: x[SEVERITY_FIELD])
    return problem_list


async def get_host_problems(host_id: int) -> list:
    async with AioZabbixApi() as aio_zabbix:
        problems = await get_zabbix_host_problems(aio_zabbix, host_id)
    return problems


def main():
    pass
    # loop = asyncio.get_event_loop()
    # # result = loop.run_until_complete(get_zabbix_monitoring_hosts([10454, 10462]))
    # result = loop.run_until_complete(get_host_details([10472, 10434]))
    # loop.close()
    # for item in result:
    #     print(item)


if __name__ == '__main__':
    main()
