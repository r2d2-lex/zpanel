from typing import Union

from pydantic import BaseModel, ConfigDict
from fastapi import Path


class Host(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    host_id: int
    column: int = Path(..., ge=0, le=3, title='Monitoring column')
    name: str

class CreateHost(Host):
    pass

class UpdateHost(CreateHost):
    pass

class UpdateHostPartial(CreateHost):
    host_id: Union[int, None] = None
    column: Union[int, None] = None
    name: Union[str, None] = None


class HostImage(Host):
    model_config = ConfigDict(from_attributes=True)
    image: str
