
async def test_create_host(client_ac):
    response = await client_ac.post('/monitor/hosts/', json={
        "host_id": 31338,
        "column": 3,
        "name": "superhost"
})
    assert response.status_code == 201
