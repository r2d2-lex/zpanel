import aiohttp
import logging
from aiohttp import ClientSession
from time import time
from exceptions import BadRequestFromApi
logger = logging.getLogger(__name__)

headers = {
    'Content-Type': 'application/json-rpc',
    'User-Agent': 'py-zabbix/1.1.7',
}


async def fetch(session: ClientSession, url: str) -> dict:
    async with session.get(url) as response:
        logger.debug(f'Status code: {response.status}')
        return await response.json()

async def post(session: ClientSession, url: str, data=None) -> dict:
    async with session.post(url, data=data, headers=headers) as response:
        logger.debug('Url: %s -> status code: %d', url, response.status)
        if response.status != 200:
            logger.error('Error response from %s: %d', url, response.status)
            raise BadRequestFromApi('Error response from %s: %d', url, response.status)
        return await response.json(content_type=None)
async def post_data(url, data):
    start = time()
    try:
        async with aiohttp.ClientSession() as session:
            json_response = await post(session, url, data)
            end = time()
            logger.debug('Got answer from %s after %.2f seconds\r\n', url, end - start)
            return json_response
    except (BadRequestFromApi, ValueError, TypeError) as post_error:
        logger.exception('Error with url: %s -> error: %s\r\n', url, post_error)
        raise BadRequestFromApi(('Error with url: %s -> error: %s\r\n', url, post_error))
