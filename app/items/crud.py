from typing import Union

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import MonitoredItem as ModelMonitoredItem
from items.schema import Item as SchemaItem, UpdateItemPartial, UpdateItem, CreateItem


# --------------------- ОПЕРАЦИИ С MonitoredItem -------------------- #

async def get_all_items(db: AsyncSession) -> list[ModelMonitoredItem]:
    result = await db.execute(select(ModelMonitoredItem))
    return result.scalars().all()

async def get_items_by_host_id(db: AsyncSession, host_id: int) -> list[ModelMonitoredItem]:
    query = select(ModelMonitoredItem).filter(ModelMonitoredItem.host_id == host_id)
    result = await db.execute(query)
    return result.scalars().all()


async def get_item(db: AsyncSession, item: SchemaItem) -> ModelMonitoredItem:
    result = await db.execute(select(ModelMonitoredItem).filter(ModelMonitoredItem.host_id == item.host_id,
                                               ModelMonitoredItem.name == item.name))
    return result.scalars().first()


async def add_item(db: AsyncSession, item: CreateItem) -> ModelMonitoredItem:
    db_item = ModelMonitoredItem(host_id=item.host_id, name=item.name, value_type=item.value_type)
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item


async def delete_item(db: AsyncSession, host_id: int, name: str) -> None:
    result = await db.execute(select(ModelMonitoredItem).filter(ModelMonitoredItem.host_id == host_id,
                                                  ModelMonitoredItem.name == name,
                                                  ))
    db_item = result.scalars().first()

    if db_item:
        await db.delete(db_item)
        await db.commit()
        return


async def update_item(
        db: AsyncSession,
        item: Union[UpdateItem, UpdateItemPartial],
        db_item: ModelMonitoredItem,
        partial = False,
) -> ModelMonitoredItem:

    for name, value in item.model_dump(exclude_unset=partial).items():
        setattr(db_item, name, value)
    await db.commit()
    await db.refresh(db_item)
    return db_item
