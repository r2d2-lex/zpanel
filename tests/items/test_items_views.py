import pytest

@pytest.fixture(scope='function')
async def create_host_for_item(client):
    await client.post('/monitor/hosts/', json={
        "host_id": 31338,
        "column": 3,
        "name": "superhost"
    })
    yield
    await client.delete('/monitor/hosts/31338')


async def test_create_item(client, create_host_for_item):
    response = await client.post('/items/', json={
        'id': 0,
        'host_id': 31338,
        'name': 'system.cpu.load[all,avg1]',
        'value_type': 'LA'
    })
    assert response.status_code == 201
    assert response.json()['host_id'] == 31338
    assert response.json()['name'] == 'system.cpu.load[all,avg1]'
    assert response.json()['value_type'] == 'LA'


async def test_get_item_correct_response(client, create_host_for_item):
    response = await client.post('/items/', json={
        'id': 0,
        'host_id': 31338,
        'name': 'system.cpu.load[all,avg1]',
        'value_type': 'LA'
    })
    item_id = response.json()['id']
    response = await client.get(f'/items/{item_id}')
    assert response.status_code == 200
    assert response.json()['host_id'] == 31338
    assert response.json()['name'] == 'system.cpu.load[all,avg1]'
    assert response.json()['value_type'] == 'LA'

async def test_get_item_returns_not_found_hostid(client):
    response = await client.get('/items/9999999')
    assert response.status_code == 404
    assert response.json()['detail'] == 'Item 9999999 not found'


async def test_update_item(client, create_host_for_item):
    response = await client.post('/items/', json={
        'id': 0,
        'host_id': 31338,
        'name': 'system.cpu.load[all,avg1]',
        'value_type': 'LA'
    })
    item_id = response.json()['id']
    response = await client.put(
        f'/items/{item_id}',
        json={
            'id': item_id,
            'host_id': 31338,
            'name': 'vm.memory.size[pavailable]',
            'value_type': '%'
        }
    )
    assert response.status_code == 200
    assert response.json() == {
            'id': item_id,
            'host_id': 31338,
            'name': 'vm.memory.size[pavailable]',
            'value_type': '%'
        }
#
async def test_update_item_partial(client, create_host_for_item):
    response = await client.post('/items/', json={
        'id': 0,
        'host_id': 31338,
        'name': 'system.cpu.load[all,avg1]',
        'value_type': 'LA'
    })
    item_id = response.json()['id']
    response = await client.patch(
        f'/items/{item_id}',
        json={
            'id': item_id,
            'host_id': 31338,
            'name': 'vm.memory.size[pavailable]',
            'value_type': '%'
        }
    )
    assert response.status_code == 200
    assert response.json() == {
            'id': item_id,
            'host_id': 31338,
            'name': 'vm.memory.size[pavailable]',
            'value_type': '%'
        }


async def test_delete_item_from_db(client, create_host_for_item):
    response = await client.post('/items/', json={
        'id': 0,
        'host_id': 31338,
        'name': 'system.cpu.load[all,avg1]',
        'value_type': 'LA'
    })
    item_id = response.json()['id']
    response = await client.delete(f'/items/{item_id}')
    assert response.status_code == 204
