import aiohttp
import logging
from aiohttp import ClientSession, ClientTimeout, ContentTypeError
from typing import Union, Optional, Dict, Any
from time import time
from exceptions import BadResponseFromApi
logger = logging.getLogger(__name__)

headers = {
    'Content-Type': 'application/json-rpc',
    'User-Agent': 'py-zabbix/1.1.7',
}


async def fetch(session: ClientSession, url: str) -> dict:
    async with session.get(url) as response:
        logger.debug(f'Status code: {response.status}')
        return await response.json()


async def post(session: ClientSession, url: str, data: Optional[Union[Dict[str, Any], bytes, str]] = None) -> Dict[str, Any]:
    post_kwargs = {'headers': headers}
    if isinstance(data, (dict, list)):
        post_kwargs['json'] = data
    else:
        post_kwargs['data'] = data

    async with session.post(url, data=data, headers=headers) as response:
        logger.debug('Url: %s -> status code: %d', url, response.status)
        if response.status != 200:
            logger.error('Error response from %s: %d', url, response.status)
            raise BadResponseFromApi(f'Error response from {url}: {response.status}')
        try:
            json_response = await response.json()
        except (ContentTypeError, ValueError) as error:
            raise BadResponseFromApi(f'Invalid JSON from {url}') from error
        return json_response


async def post_data(url:str, data: Optional[Union[Dict[str, Any], bytes, str]] = None) -> Dict[str, Any]:
    start = time()
    timeout = ClientTimeout(total=10)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            json_response = await post(session, url, data)
            logger.debug('Got answer from %s after %.2f seconds\r\n', url, time() - start)
            return json_response
    except (BadResponseFromApi, ValueError, TypeError) as post_error:
        logger.exception('Error with url: %s', url)
        raise BadResponseFromApi(f'Error with url: {url} -> error: {post_error}\r\n') from post_error
