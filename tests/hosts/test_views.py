import pytest

@pytest.fixture(scope='function')
async def create_host(client):
    response = await client.post('/monitor/hosts/', json={
        "host_id": 31338,
        "column": 3,
        "name": "superhost"
})
    yield response
    await client.delete('/monitor/hosts/31338')


async def test_create_host(client, create_host):
    response = create_host
    assert response.status_code == 201


async def test_get_host_correct_response(client, create_host):
    response = await client.get('/monitor/hosts/31338')
    assert response.json() == {
        "host_id": 31338,
        "column": 3,
        "name": "superhost"
    }

async def test_get_host_returns_not_found_hostid(client):
    response = await client.get('/monitor/hosts/9999999')
    assert response.json()['detail'] == 'Host 9999999 not found'


async def test_update_host(client, create_host):
    response = await client.put(
        '/monitor/hosts/31338',
        json={
            "host_id": 31338,
            "column": 1,
            "name": "megahost"
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "host_id": 31338,
        "column": 1,
        "name": "megahost"
    }

async def test_update_host_partial(client, create_host):
    response = await client.patch(
        '/monitor/hosts/31338',
        json={
            "host_id": 31338,
            "column": 1,
            "name": "megahost"
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "host_id": 31338,
        "column": 1,
        "name": "megahost"
    }


async def test_delete_host_from_db(client, create_host):
    response = await client.delete('/monitor/hosts/31338')
    assert response.status_code == 204
