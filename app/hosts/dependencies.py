import logging
from typing import Annotated

from fastapi import HTTPException, status, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from hosts import crud
from models import Host


async def host_by_id(
        host_id: Annotated[int, Path],
        db: AsyncSession = Depends(get_db)
) -> Host:
    db_host = await crud.get_host(db=db, host_id=host_id)
    if db_host is not None:
        return db_host
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Host {host_id} not found"
    )
