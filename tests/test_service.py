from unittest.mock import patch, AsyncMock


from models import MonitoredItem
from service import get_data_items

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
