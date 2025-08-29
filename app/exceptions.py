import aiohttp


class BadRequestFromApi(aiohttp.ClientError):
    pass
