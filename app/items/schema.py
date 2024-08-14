from pydantic import BaseModel, ConfigDict


class Item(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    host_id: int
    name: str
    value_type: str

class CreateItem(Item):
    pass

class UpdateItem(CreateItem):
    pass

class UpdateItemPartial(CreateItem):
    pass
