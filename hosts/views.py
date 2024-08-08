from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import crud
from db import get_db
from schema import Host

router = APIRouter(prefix='/monitor/hosts', tags=['hosts'])

# Хосты, которые будут мониторится
@router.get('/', response_model=list[Host])
async def read_host_from_db(db: AsyncSession = Depends(get_db)):
    hosts = await crud.get_monitored_hosts(db)
    return hosts


@router.get('/{host_id}', response_model=Host)
async def get_host_from_db(host_id: int, db: AsyncSession = Depends(get_db)):
    db_host = await crud.get_host(db=db, host_id=host_id)
    if not db_host:
        raise HTTPException(status_code=404, detail="Host not found")
    return db_host


@router.post('/', response_model=Host)
async def add_host_to_db(host: Host, db: AsyncSession = Depends(get_db)):
    db_host = await crud.get_host(db=db, host_id=host.host_id)
    if db_host:
        return await crud.update_host(db=db, host=host)
    return await crud.add_host(host=host, db=db)


@router.delete('/', response_model=Host)
async def delete_host_from_db(host: Host, db: AsyncSession = Depends(get_db)):
    db_host = await crud.get_host(db=db, host_id=host.host_id)
    if not db_host:
        raise HTTPException(status_code=400, detail="Host not found")
    return await crud.delete_host(db=db, host_id=host.host_id)


@router.patch('/', response_model=Host)
async def update_host_from_db(host: Host, db: AsyncSession = Depends(get_db)):
    db_host = await crud.get_host(db=db, host_id=host.host_id)
    if not db_host:
        raise HTTPException(status_code=400, detail="Host not found")
    return await crud.update_host(db=db, host=host)
