from unittest.mock import patch, AsyncMock
from models import MonitoredItem

async def test_index(client):
    response = await client.get('/')
    assert response.status_code == 200
    assert 'js/index.js' in response.text
    assert 'Настройка' in response.text

async def test_ajax_settings(client):
    with patch('AioZabbix.get_all_zabbix_monitoring_hosts', new_callable=AsyncMock) as mock_get_all_zabbix_mh, \
            patch('service.get_host_details', new_callable=AsyncMock) as mock_get_hosts_details:
        mock_get_all_zabbix_mh.return_value = [
            {'host':'node1011', 'hostid':'99632', 'name':'node1011'},
            {'host':'node1012', 'hostid':'99633', 'name':'node1012'},
        ]
        mock_get_hosts_details.return_value =  [
            {'host':'node1011', 'hostid':'99632', 'name':'node1', 'column': 1},
            {'host':'node1012', 'hostid':'99633', 'name':'node2', 'column': 2},
        ]
        response = await client.get('/settings')
        assert response.status_code == 200
        assert 'node1011' in response.text
        assert 'node1012' in response.text
        assert '99632' in response.text
        assert '99633' in response.text
        mock_get_all_zabbix_mh.assert_awaited_once()
        mock_get_hosts_details.assert_awaited_once()


async def test_ajax_get_host_items(client):
    with patch('items.views.get_item_by_host_id', new_callable=AsyncMock, return_value=MonitoredItem(
        id=9991,
        host_id=1001,
        name='vm.memory.size[pavailable]',
        value_type='%mem',
    )):
        response = await client.get('/data-items/1001')
        assert response.status_code == 200
        assert 'vm.memory.size[pavailable]' in response.text
        assert '%mem' in response.text
        assert '1001' in response.text
        assert '9991' in response.text
