from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

import items.crud as crud
from items.dependencies import get_item_by_id
from items.schema import Item, CreateItem, UpdateItem, UpdateItemPartial
from db import get_db
from models import MonitoredItem

router = APIRouter(prefix='/items', tags=['items'])


@router.get('/', response_model=list[Item])
async def get_all_items(db: AsyncSession = Depends(get_db)):
    return await crud.get_all_items(db)


@router.get('/{item_id}', response_model=Item)
async def get_item_by_id(
        item: MonitoredItem = Depends(get_item_by_id)
):
    return item


@router.get('/{host_id}', response_model=list[Item])
async def get_item_by_host_id(host_id: int, db: AsyncSession = Depends(get_db)):
    items = await crud.get_items_by_host_id(db, host_id)
    return items


@router.post(
    '/',
    response_model=Item,
    status_code=status.HTTP_201_CREATED
)
async def add_item_to_db(item: CreateItem, db: AsyncSession = Depends(get_db)):
    return await crud.add_item(item=item, db=db)


@router.put('/{item_id}', response_model=Item)
async def update_item(
        item: UpdateItem,
        db_item: MonitoredItem = Depends(get_item_by_id),
        db: AsyncSession = Depends(get_db)
):
    return await crud.update_item(db=db, db_item=db_item, item = item)


@router.patch('/{item_id}', response_model=Item)
async def update_item_partial(
        item: UpdateItemPartial,
        db_item: MonitoredItem = Depends(get_item_by_id),
        db: AsyncSession = Depends(get_db)
):
    return await crud.update_item(db=db, db_item=db_item, item = item, partial=True)


@router.delete('/{item_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_item_from_db(
        db_item: MonitoredItem = Depends(get_item_by_id),
        db: AsyncSession = Depends(get_db),
):
    await crud.delete_item(db=db, db_item=db_item)
