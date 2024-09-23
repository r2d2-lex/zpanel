from unittest.mock import patch, AsyncMock
from AioZabbix import get_zabbix_monitoring_hosts

from AioZabbix import AioZabbixApi


class TestAioZabbixApi:

    @patch('AioZabbix.post_data', new_callable=AsyncMock)
    async def test_zabbix_login(self, mock_post_data):
        mock_post_data.return_value = {'result': 'mock_auth_token'}

        async with AioZabbixApi() as api:
            auth_token = await api.zabbix_login()
            assert auth_token == 'mock_auth_token'
            assert api._zabbix_auth == 'mock_auth_token'

    @patch('AioZabbix.post_data', new_callable=AsyncMock)
    async def test_zabbix_logout(self, mock_post_data):
        mock_post_data.return_value = {'result': True}

        async with AioZabbixApi() as api:
            await api.zabbix_login()
            result = await api.zabbix_logout()
            assert result is True

    @patch('AioZabbix.post_data', new_callable=AsyncMock)
    async def test_zabbix_host_get(self, mock_post_data):
        mock_post_data.return_value = {'result': [{'hostid': '1', 'host': 'host1'}]}

        async with AioZabbixApi() as api:
            hosts = await api.zabbix_host_get({'output': ['hostid', 'host']})
            assert hosts == [{'hostid': '1', 'host': 'host1'}]

    @patch('AioZabbix.post_data', new_callable=AsyncMock)
    async def test_zabbix_problem_get(self, mock_post_data):
        mock_post_data.return_value = {'result': [{'eventid': '1', 'name': 'Problem 1'}]}

        async with AioZabbixApi() as api:
            problems = await api.zabbix_problem_get({'hostids': '1'})
            assert problems == [{'eventid': '1', 'name': 'Problem 1'}]

    @patch('AioZabbix.post_data', new_callable=AsyncMock)
    async def test_zabbix_item_get(self, mock_post_data):
        mock_post_data.return_value = {'result': [{'key_': 'item1', 'lastvalue': '42'}]}

        async with AioZabbixApi() as api:
            items = await api.zabbix_item_get({'hostids': '1'})
            assert items == [{'key_': 'item1', 'lastvalue': '42'}]

    @patch('AioZabbix.post_data', new_callable=AsyncMock)
    async def test_get_item_by_key(self, mock_post_data):
        mock_post_data.return_value = {'result': [{'lastvalue': '42'}]}

        async with AioZabbixApi() as api:
            value = await api.get_item_by_key(['1'], 'item1')
            assert value == [{'lastvalue': '42'}]

    @patch('AioZabbix.post_data', new_callable=AsyncMock)
    async def test_get_host_item_value(self, mock_post_data):
        mock_post_data.return_value = {'result': [{'lastvalue': '42'}]}

        async with AioZabbixApi() as api:
            value = await api.get_host_item_value(['1'], 'item1')
            assert value == '42'

    @patch('AioZabbix.post_data', new_callable=AsyncMock)
    async def test_get_host_problem(self, mock_post_data):
        mock_post_data.return_value = {'result': [{'eventid': '1', 'name': 'Problem 1'}]}

        async with AioZabbixApi() as api:
            problems = await api.get_host_problem('1')
            assert problems == [{'eventid': '1', 'name': 'Problem 1'}]

    @patch('AioZabbix.post_data', new_callable=AsyncMock)
    async def test_get_monitored_hosts(self, mock_post_data):
        mock_post_data.return_value = {'result': [{'hostid': '1', 'host': 'host1'}]}

        async with AioZabbixApi() as api:
            hosts = await api.get_monitored_hosts(['1'])
            assert hosts == [{'hostid': '1', 'host': 'host1'}]
