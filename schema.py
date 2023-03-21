from pydantic import BaseModel
from typing import Union


class Host(BaseModel):
    hostid: int
    column: int

    class Config:
        orm_mode = True


class Problem(BaseModel):
    hostid: int
    name: str
    eventid: int
    clock: str
    severity: int