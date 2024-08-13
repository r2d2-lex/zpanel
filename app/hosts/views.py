from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import hosts.crud as crud
from hosts.dependencies import host_by_id
from hosts.schema import Host, CreateHost, UpdateHost, UpdateHostPartial
from db import get_db

router = APIRouter(prefix='/monitor/hosts', tags=['hosts'])

async def get_host_by_id(session, host_id):
    db_host = await crud.get_host(db=session, host_id=host_id)
    if not db_host:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Host not found")
    return db_host


# Хосты, которые будут мониторится
@router.get('/', response_model=list[Host])
async def read_host_from_db(db: AsyncSession = Depends(get_db)):
    hosts = await crud.get_monitored_hosts(db)
    return hosts


@router.get('/{host_id}', response_model=Host)
async def get_host_from_db(
        host: Host = Depends(host_by_id),
):
    return host


@router.post(
    '/',
    response_model=Host,
    status_code=status.HTTP_201_CREATED
)
async def add_host_to_db(host: CreateHost, db: AsyncSession = Depends(get_db)):
    return await crud.add_host(host=host, db=db)


@router.put('/', response_model=Host)
async def update_host(
        host: UpdateHost,
        db: AsyncSession = Depends(get_db)
):
    db_host = await get_host_by_id(db, host.host_id)
    return await crud.update_host(host=host, db=db, db_host=db_host)


@router.patch('/', response_model=Host)
async def update_host_partial(
        host: UpdateHostPartial,
        db: AsyncSession = Depends(get_db)
):
    db_host = await get_host_by_id(db, host.host_id)
    return await crud.update_host(host=host, db=db, db_host=db_host, partial=True)


@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_host_from_db(
        host: Host,
        db: AsyncSession = Depends(get_db)
) -> None:
    db_host = await get_host_by_id(db, host.host_id)
    await crud.delete_host(db=db, host=db_host)
    return
