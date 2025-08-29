import aiohttp


class BadRequestFromApi(aiohttp.ClientError):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"{self.__class__.__name__}: {self.message}"
