from typing import Union

from pydantic import BaseModel, ConfigDict


class Item(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    host_id: int
    name: str
    value_type: str

class CreateItem(Item):
    pass

class UpdateItem(CreateItem):
    pass

class UpdateItemPartial(CreateItem):
    id: Union[int, None] = None
    host_id: Union[int, None] = None
    name: Union[str, None] = None
    value_type: Union[str, None] = None
