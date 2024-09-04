from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch, AsyncMock

from conftest import override_get_db
from monitoring.views import get_monitored_hosts_ids
from models import Host


async def test_get_monitored_hosts_ids_returns_correct_values(db: AsyncSession = Depends(override_get_db)):
    with patch('hosts.crud.get_monitored_hosts', new_callable=AsyncMock) as mock_get_monitored_hosts:
        mock_get_monitored_hosts.return_value=[
            Host(
                host_id=1,
                column=1,
                image='image1.png',
                name='node1',
            ),
            Host(
                host_id=2,
                column=2,
                image='image2.png',
                name='node2',
            ),
            Host(
                host_id=3,
                column=0,
                image='image3.png',
                name='node3',
            ),
    ]
        result = await get_monitored_hosts_ids(db)
        assert result == [1, 2]


async def test_monitoring(client):
    response = await client.get('/monitoring')
    assert response.status_code == 200
    assert 'Мониторинг' in response.text


async def test_ajax_monitoring_panel(client):
    # with patch('get_monitored_hosts_ids', new_callable=AsyncMock, return_value=[10000, 10001, 10002]), \
    with patch('AioZabbix.get_zabbix_monitoring_hosts', new_callable=AsyncMock, return_value=[
            {'hostid': '10000', 'host': 'node0', 'name': 'node0', 'interfaces': [{'ip': '172.20.0.4'}]},
            {'hostid': '10001', 'host': 'node1', 'name': 'node1', 'interfaces': [{'ip': '172.20.0.5'}]},
            {'hostid': '10002', 'host': 'node2', 'name': 'node2', 'interfaces': [{'ip': '172.20.0.6'}]},
        ]), \
        patch('service.get_host_details', new_callable=AsyncMock, return_value=[
            {'hostid': '10000', 'host': 'node0', 'name': 'node0', 'interfaces': [{'ip': '172.20.0.4'}], 'image': 'node0.png',
             'problems': [
                 {'eventid': '001', 'clock': '2024-01-02 12:30:30', 'name': 'Postgres shutdown on node0',
                  'severity': '4'},
                 {'eventid': '002', 'clock': '2024-01-02 12:30:30', 'name': '1c RAgent shutdown on node0',
                  'severity': '4'},
                 {'eventid': '003', 'clock': '2024-01-02 12:30:30', 'name': '1c Ras shutdown on node0',
                  'severity': '4'},
                 {'eventid': '004', 'clock': '2024-01-02 12:30:30', 'name': '1c rmngr shutdown on node0',
                  'severity': '4'},
             ], 'column': 1},

            {'hostid': '10001', 'host': 'node1', 'name': 'node1', 'interfaces': [{'ip': '172.20.0.5'}],
             'data_items': [
                 {'item_value': '1.2', 'item_type': 'LA'},
                 {'item_value': '53', 'item_type': '%'}],
             'image': 'node1.png', 'problems': [], 'column': 2},

            {'hostid': '10002', 'host': 'node2', 'name': 'node2', 'interfaces': [{'ip': '172.20.0.6'}], 'image': 'node2.png',
             'problems': [], 'column': 3}
    ]
              ):
        response = await client.get('/panel/')
        assert response.status_code == 200
        check_text = ['node0', 'node1', 'node2',
                      '10000', '10001', '10002',
                      '172.20.0.4', '172.20.0.5', '172.20.0.6',
                      'Postgres shutdown on node0', '1c RAgent shutdown on node0',
                      ]
        for text in check_text:
            assert text in response.text
