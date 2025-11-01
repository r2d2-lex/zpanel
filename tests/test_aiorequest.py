import aiohttp
import pytest
from aioresponses import aioresponses
from aiorequest import post, post_data

import os


# def test_environment_variable():
#     assert 'PYTHONPATH' in os.environ
#     print(os.environ['PYTHONPATH'])


@pytest.mark.asyncio
async def test_post():
    url = 'http://example.com/api'
    data = {'key': 'value'}
    expected_response = {'result': 'success'}

    with aioresponses() as m:
        m.post(url, payload=expected_response)

        async with aiohttp.ClientSession() as session:
            response = await post(session, url, data)
            assert response == expected_response


@pytest.mark.asyncio
async def test_post_data():
    url = 'http://example.com/api'
    data = {'key': 'value'}
    expected_response = {'result': 'success'}

    with aioresponses() as m:
        m.post(url, payload=expected_response)

        response = await post_data(url, data)
        assert response == expected_response
