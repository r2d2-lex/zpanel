from pydantic import BaseModel
from fastapi import Path


class HostId(BaseModel):
    host_id: int


class Host(HostId):
    column: int = Path(..., ge=0, le=3, title='Monitoring column')
    name: str

    class Config:
        orm_mode = True


class HostImage(Host):
    image: str

    class Config:
        orm_mode = True


class Item(BaseModel):
    host_id: int
    name: str
    value_type: str

    class Config:
        orm_mode = True
