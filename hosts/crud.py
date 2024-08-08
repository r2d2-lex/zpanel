from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from hosts.schema import Host as SchemaHost
from hosts.schema import HostImage as SchemaImageHost
from models import Host as ModelHost


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
    result = await db.execute(select(ModelHost).filter(ModelHost.host_id == host.host_id))
    db_host = result.scalars().first()
    if db_host:
        await db.execute(update(ModelHost).filter(ModelHost.host_id == host.host_id), ({'image': image_name}))
        await db.commit()
        await db.refresh(db_host)
    return db_host
