import aiohttp
from aiohttp import ClientSession
from time import time
import logging
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
        logger.debug(f'Status code: {response.status}')
        return await response.json(content_type=None)


async def post_data(url, data):
    logger.debug(f'Starting with {url}')
    start = time()
    try:
        async with aiohttp.ClientSession() as session:
            json = await post(session, url, data)
            end = time()
            logger.debug(f'Got answer from {url} after {end-start}')

    except Exception as err:
        logger.exception(f'Error with {url} error: {err}')
        return 'error'

    return json
