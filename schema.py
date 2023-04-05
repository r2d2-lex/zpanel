from pydantic import BaseModel
from fastapi import Path


class Host(BaseModel):
    hostid: int
    column: int = Path(..., ge=0, le=3, title='Monitoring column')

    class Config:
        orm_mode = True


class HostImage(BaseModel):
    hostid: int
    column: int = Path(..., ge=0, le=3, title='Monitoring column')
    image: str

    class Config:
        orm_mode = True
