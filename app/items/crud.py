from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from models import MonitoredItem as ModelMonitoredItem
from items.schema import Item as SchemaItem

# --------------------- ОПЕРАЦИИ С MonitoredItem -------------------- #

async def get_items(db: AsyncSession, host_id: int):
    query = select(ModelMonitoredItem).filter(ModelMonitoredItem.host_id == host_id)
    result = await db.execute(query)
    return result.scalars().all()


async def get_item(db: AsyncSession, item: SchemaItem):
    result = await db.execute(select(ModelMonitoredItem).filter(ModelMonitoredItem.host_id == item.host_id,
                                               ModelMonitoredItem.name == item.name))
    return result.scalars().first()


async def add_item(db: AsyncSession, item: SchemaItem):
    db_item = ModelMonitoredItem(host_id=item.host_id, name=item.name, value_type=item.value_type)
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item


async def delete_item(db: AsyncSession, host_id: int, name: str):
    result = await db.execute(select(ModelMonitoredItem).filter(ModelMonitoredItem.host_id == host_id,
                                                  ModelMonitoredItem.name == name,
                                                  ))
    db_item = result.scalars().first()

    if db_item:
        await db.delete(db_item)
        await db.commit()
    return db_item


async def update_item(db: AsyncSession, item: SchemaItem):
    result = await db.execute(select(ModelMonitoredItem).filter(ModelMonitoredItem.host_id == item.host_id))
    db_item = result.scalars().first()
    if db_item:
        await db.execute(update(ModelMonitoredItem).filter(ModelMonitoredItem.host_id == item.host_id,
                                            ModelMonitoredItem.name == item.name,
                                            ), item.dict())
        await db.commit()
        await db.refresh(db_item)
    return db_item
