from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from models import Host as ModelHost
from models import MonitoredItem as ModelMonitoredItem
from schema import Item as SchemaItem
from schema import Host as SchemaHost
from schema import HostImage as SchemaImageHost


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


# --------------------- ОПЕРАЦИИ С Host -------------------- #

async def get_monitored_hosts(db: AsyncSession):
    result = await db.execute(select(ModelHost))
    return result.scalars().all()


async def get_host(db: AsyncSession, host_id: int):
    result = await db.execute(select(ModelHost).filter(ModelHost.host_id == host_id))
    return result.scalars().first()


async def add_host(db: AsyncSession, host: SchemaHost):
    db_host = ModelHost(host_id=host.host_id, column=host.column, name=host.name)
    db.add(db_host)
    await db.commit()
    await db.refresh(db_host)
    return db_host


async def delete_host(db: AsyncSession, host_id: int):
    result = await db.execute(select(ModelHost).filter(ModelHost.host_id == host_id))
    db_host = result.scalars().first()
    if db_host:
        await db.delete(db_host)
        await db.commit()
    return db_host


async def update_host(db: AsyncSession, host: SchemaHost):
    result = await db.execute(select(ModelHost).filter(ModelHost.host_id == host.host_id))
    db_host = result.scalars().first()
    if db_host:
        await db.execute(update(ModelHost).filter(ModelHost.host_id == host.host_id), host.dict())
        await db.commit()
        await db.refresh(db_host)
    return db_host


async def update_host_image(db: AsyncSession, host: SchemaImageHost, image_name: str):
    db_host = db.query(ModelHost).filter(ModelHost.host_id == host.host_id).first()
    if db_host:
        db.query(ModelHost).filter(ModelHost.host_id == host.host_id).update({'image': image_name})
        await db.commit()
        await db.refresh(db_host)
    return db_host
