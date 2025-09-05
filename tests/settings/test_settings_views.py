from unittest.mock import patch, AsyncMock
from models import MonitoredItem
from items.views import get_item_by_host_id
from auth.views import get_auth_user_username
from conftest import app

TEST_USERNAME = 'test'

def mock_get_auth_user_username():
    return TEST_USERNAME

app.dependency_overrides.update({get_auth_user_username: mock_get_auth_user_username})

async def test_index(client):
    response = await client.get('/')
    assert response.status_code == 200
    assert 'js/index.js' in response.text
    assert 'Настройка' in response.text
    assert TEST_USERNAME in response.text

async def test_ajax_settings(client):
    with patch('settings.views.get_all_zabbix_monitoring_hosts', new_callable=AsyncMock) as mock_get_all_zabbix_mh, \
            patch('settings.views.get_host_details', new_callable=AsyncMock) as mock_get_hosts_details:
        mock_get_all_zabbix_mh.return_value = [
            {'host':'node1011', 'hostid':'99632', 'name':'node1011'},
            {'host':'node1012', 'hostid':'99633', 'name':'node1012'},
        ]
        mock_get_hosts_details.return_value =  ([
            {'host':'node1011', 'hostid':'99632', 'name':'node1', 'column': 1},
            {'host':'node1012', 'hostid':'99633', 'name':'node2', 'column': 2},
        ],  [] # Host details problem was here
        )
        response = await client.get('/settings')
        assert response.status_code == 200
        assert 'node1011' in response.text
        assert 'node1012' in response.text
        assert '99632' in response.text
        assert '99633' in response.text
        mock_get_all_zabbix_mh.assert_awaited_once()
        mock_get_hosts_details.assert_awaited_once()

async def mock_get_item_by_host_id():
    return [MonitoredItem(
        id=9991,
        host_id=1001,
        name='vm.memory.size[pavailable]',
        value_type='%mem',
    ),]
app.dependency_overrides[get_item_by_host_id] = mock_get_item_by_host_id

async def test_ajax_get_host_items(client):
    response = await client.get('/data-items/1001')
    assert response.status_code == 200
    assert 'vm.memory.size[pavailable]' in response.text
    assert '%mem' in response.text
    assert '9991' in response.text
