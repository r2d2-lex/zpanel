from pydantic import BaseModel
from typing import Union


class Host(BaseModel):
    hostid: int
    host: str
    name: str
    error: str  # Error message
    snmp_error: str # SNMP error message
    # is_offer: Union[bool, None] = None


class Problem(BaseModel):
    hostid: int
    name: str
    eventid: int
    clock: str
    severity: int