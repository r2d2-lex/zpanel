import asyncio
import config
import json
import logging

from aiorequest import post_data

logging.basicConfig(level=config.LOGGING_LEVEL)

headers = {
    'Content-Type': 'application/json-rpc',
    'User-Agent': 'py-zabbix/1.1.7',
}

ZABBIX_API_URL = config.ZABBIX_API_URL + 'api_jsonrpc.php'


async def zabbix_request(method: str, params=None, auth=None):
    if auth:
        params.update({'auth': auth})
    request_json = {
        'jsonrpc': '2.0',
        'method': method,
        'params': params or {},
        'id': '1',
    }
    data = json.dumps(request_json)
    if not isinstance(data, bytes):
        data = data.encode("utf-8")

    result_data = await post_data(ZABBIX_API_URL, data)
    return result_data


async def zabbix_login(user, password):
    method = 'user.login'
    params = {'user': user, 'password': password}
    result = await zabbix_request(method, params=params)
    auth = result['result']
    return auth


def main():
    loop = asyncio.get_event_loop()
    auth = loop.run_until_complete(zabbix_login(config.ZABBIX_API_USER, config.ZABBIX_API_PASSWORD))
    loop.close()
    print('Auth: ', auth)


if __name__ == '__main__':
    main()
