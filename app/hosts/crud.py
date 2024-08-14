import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional, Union

from hosts.schema import CreateHost, UpdateHostPartial, UpdateHost, Host as Host_Schema
from hosts.schema import HostImage as SchemaImageHost
from models import Host as ModelHost


# --------------------- ОПЕРАЦИИ С Host -------------------- #

async def get_monitored_hosts(db: AsyncSession) -> list[ModelHost]:
    result = await db.execute(select(ModelHost))
    return result.scalars().all()


async def get_host(db: AsyncSession, host_id: int) -> Optional[ModelHost]:
    return await db.get(ModelHost, host_id)


async def add_host(db: AsyncSession, host: CreateHost) -> ModelHost:
    db_host = ModelHost(**host.dict())
    db.add(db_host)
    await db.commit()
    await db.refresh(db_host)
    return db_host


async def delete_host(db: AsyncSession, host: Host_Schema) -> None:
    await db.delete(host)
    await db.commit()
    return


async def update_host(
        db: AsyncSession,
        host: Union[UpdateHost, UpdateHostPartial],
        db_host = ModelHost,
        partial = False,
) -> ModelHost:
    for name, value in host.model_dump(exclude_unset=partial).items():
        setattr(db_host, name, value)
    await db.commit()
    return db_host


async def update_host_image(db: AsyncSession, host: SchemaImageHost, image_name: str):
    result = await db.execute(select(ModelHost).filter(ModelHost.host_id == host.host_id))
    db_host = result.scalars().first()
    if db_host:
        await db.execute(update(ModelHost).filter(ModelHost.host_id == host.host_id), ({'image': image_name}))
        await db.commit()
        await db.refresh(db_host)
    return db_host
