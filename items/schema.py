from pydantic import BaseModel

class Item(BaseModel):
    host_id: int
    name: str
    value_type: str

    class Config:
        orm_mode = True
