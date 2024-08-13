from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import hosts.crud as crud
from hosts.dependencies import host_by_id
from hosts.schema import Host, CreateHost, UpdateHost, UpdateHostPartial
from db import get_db

router = APIRouter(prefix='/monitor/hosts', tags=['hosts'])


# Хосты, которые будут мониторится
@router.get('/', response_model=list[Host])
async def read_host_from_db(db: AsyncSession = Depends(get_db)):
    hosts = await crud.get_monitored_hosts(db)
    return hosts


@router.get('/{host_id}', response_model=Host)
async def get_host_from_db(
        db_host: Host = Depends(host_by_id),
):
    return db_host


@router.post(
    '/',
    response_model=Host,
    status_code=status.HTTP_201_CREATED
)
async def add_host_to_db(host: CreateHost, db: AsyncSession = Depends(get_db)):
    return await crud.add_host(host=host, db=db)


@router.put('/{host_id}', response_model=Host)
async def update_host(
        host: UpdateHost,
        db_host: Host = Depends(host_by_id),
        db: AsyncSession = Depends(get_db)
):
    return await crud.update_host(host=host, db=db, db_host=db_host)


@router.patch('/{host_id}', response_model=Host)
async def update_host_partial(
        host: UpdateHostPartial,
        db_host: Host = Depends(host_by_id),
        db: AsyncSession = Depends(get_db)
):
    return await crud.update_host(host=host, db=db, db_host=db_host, partial=True)


@router.delete('/{host_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_host_from_db(
        db_host: Host = Depends(host_by_id),
        db: AsyncSession = Depends(get_db)
) -> None:
    await crud.delete_host(db=db, host=db_host)
    return
