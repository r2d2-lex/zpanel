import asyncio
import config
import json
import logging

from aiorequest import post_data

logging.basicConfig(level=config.LOGGING_LEVEL)


class AioZabbixApi:

    def __init__(self):
        self.zabbix_api_url = config.ZABBIX_API_URL + 'api_jsonrpc.php'
        self._zabbix_auth = None

    def __str__(self):
        return 'ZabbixMonitoring'

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
        logging.info(f'Method {method} Request json {request_json}...')

        data = json.dumps(request_json)
        if not isinstance(data, bytes):
            data = data.encode("utf-8")

        result_data = await post_data(self.zabbix_api_url, data)

        try:
            result = result_data['result']
        except KeyError as error:
            logging.info(f'Method: {method} error {error}...')
        return result

    async def zabbix_host_get(self, params):
        method = 'host.get'
        return await self._zabbix_request(method, params=params)

    async def zabbix_login(self):
        method = 'user.login'
        params = {'user': config.ZABBIX_API_USER, 'password': config.ZABBIX_API_PASSWORD}
        self._zabbix_auth = await self._zabbix_request(method, params=params)
        return self._zabbix_auth

    async def zabbix_logout(self):
        method = 'user.logout'
        return await self._zabbix_request(method)

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
    aio_zabbix = AioZabbixApi()
    await aio_zabbix.zabbix_login()
    hosts = await aio_zabbix.get_monitored_hosts(host_ids)
    await aio_zabbix.zabbix_logout()
    return hosts


async def main_async():
    aio_zabbix = AioZabbixApi()
    auth = await aio_zabbix.zabbix_login()
    params = {'status': 1, 'monitored_hosts': 1, 'selectInterfaces': ['ip'], }
    hosts = await aio_zabbix.zabbix_host_get(params)
    exit = await aio_zabbix.zabbix_logout()
    print(f'{auth} {hosts} {exit}')


def main():
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(get_zabbix_monitoring_hosts([10454, 10462]))
    loop.close()
    print(result)


if __name__ == '__main__':
    main()
