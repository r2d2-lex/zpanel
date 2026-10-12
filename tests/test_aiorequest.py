from contextlib import asynccontextmanager
import aiohttp
import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer
from aiorequest import post, post_data

@asynccontextmanager
async def api_server(expected_data, response_data):
    async def handler(request):
        assert await request.json() == expected_data
        return web.json_response(response_data)
    app = web.Application()
    app.router.add_post("/api", handler)
    server = TestServer(app)
    await server.start_server()
    try:
        yield str(server.make_url("/api"))
    finally:
        await server.close()

@pytest.mark.asyncio
async def test_post():
    data = {'key': 'value'}
    expected_response = {'result': 'success'}

    async with api_server(data, expected_response) as url:
        async with aiohttp.ClientSession() as session:
            response = await post(session, url, data)
            assert response == expected_response


@pytest.mark.asyncio
async def test_post_data():
    data = {'key': 'value'}
    expected_response = {'result': 'success'}

    async with api_server(data, expected_response) as url:
        response = await post_data(url, data)
        assert response == expected_response
