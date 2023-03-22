from pydantic import BaseModel
from fastapi import Path
from typing import Union


class Host(BaseModel):
    hostid: int
    column: int = Path(..., ge=0, le=3, title='Monitoring column')

    class Config:
        orm_mode = True


class Problem(BaseModel):
    hostid: int
    name: str
    eventid: int
    clock: str
    severity: int