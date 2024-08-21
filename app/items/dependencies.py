from fastapi import Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from items import crud
from models import MonitoredItem


async def get_item_by_id(
        item_id: int,
        db: AsyncSession = Depends(get_db)
) -> MonitoredItem:
    item = await crud.get_item_by_id(db, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {item_id} not found")
    return item
