from unittest.mock import patch, AsyncMock


from models import MonitoredItem
from service import get_data_items, get_async_host_details
from models import Host as ModelHost

class MockAioZabbixApi:
    async def get_host_item_value(self, host_ids: list, item_name: str) -> str:
        if item_name == 'system.cpu.load[all,avg1]':
            return '1.2'
        elif item_name == 'net.if.out["eth0"]':
            return '2472'
        else:
            return ''

async def test_get_data_items():
    mock_db = AsyncMock()
    mock_api = MockAioZabbixApi()

    with patch('service.get_items_by_host_id', new_callable=AsyncMock, return_value=[
        MonitoredItem(id=1, host_id=1001, name='system.cpu.load[all,avg1]', value_type='%'),
        MonitoredItem(id=2, host_id=1001, name='net.if.out["eth0"]', value_type=''),
    ]):
        result = await get_data_items(mock_db, mock_api, 1001)
        assert result == [
            {'item_value': '1.2', 'item_type': '%'},
            {'item_value': '2472', 'item_type': ''},
        ]


async def test_get_async_host_details():
    api = AsyncMock()
    zabbix_host = {'host':'node1011', 'hostid':'99632', 'name':'node1', 'column': 1}
    db = AsyncMock()
    monitoring_hosts = []
    with_problems = True

    with patch('service.get_host', new_callable=AsyncMock,
               return_value=ModelHost(
                   host_id=99632,
                   column=1,
                   image='image.png',
                   name='node1')):
        with patch('service.get_data_items', new_callable=AsyncMock, return_value=[
            {'item_value': '1.2', 'item_type': '%'},
            {'item_value': '2472', 'item_type': ''},
        ]):
            with patch('service.get_zabbix_host_problems', new_callable=AsyncMock,
                       return_value=[
        {'eventid': '001', 'clock': '2024-01-02 12:30:30', 'name': 'Postgres shutdown on node0', 'severity': '4'},
        {'eventid': '002', 'clock': '2024-01-02 12:30:30', 'name': '1c RAgent shutdown on node0', 'severity': '4'},
        {'eventid': '003', 'clock': '2024-01-02 12:30:30', 'name': '1c Ras shutdown on node0', 'severity': '4'},
        {'eventid': '004', 'clock': '2024-01-02 12:30:30', 'name': '1c rmngr shutdown on node0', 'severity': '4'}
                       ]):
                await get_async_host_details(api, zabbix_host, db, monitoring_hosts, with_problems)
                assert monitoring_hosts[0]['hostid'] == '99632'
                assert monitoring_hosts[0]['column'] == 1
                assert monitoring_hosts[0]['name'] == 'node1'
                assert monitoring_hosts[0]['data_items'] == [ {'item_value': '1.2', 'item_type': '%'},
                                                              {'item_value': '2472', 'item_type': ''},
                                                              ]
                assert monitoring_hosts[0]['image'] == 'image.png'
                assert monitoring_hosts[0]['problems'] == [
        {'eventid': '001', 'clock': '2024-01-02 12:30:30', 'name': 'Postgres shutdown on node0', 'severity': '4'},
        {'eventid': '002', 'clock': '2024-01-02 12:30:30', 'name': '1c RAgent shutdown on node0', 'severity': '4'},
        {'eventid': '003', 'clock': '2024-01-02 12:30:30', 'name': '1c Ras shutdown on node0', 'severity': '4'},
        {'eventid': '004', 'clock': '2024-01-02 12:30:30', 'name': '1c rmngr shutdown on node0', 'severity': '4'}
                       ]
