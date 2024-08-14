from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

import items.crud as crud
from items.schema import Item, CreateItem, UpdateItemPartial
from db import get_db

router = APIRouter(prefix='/items', tags=['items'])

@router.get('/', response_model=list[Item])
async def get_all_items(db: AsyncSession = Depends(get_db)):
    return await crud.get_all_items(db)


@router.get('/{host_id}', response_model=list[Item])
async def get_item_from_db(host_id: int, db: AsyncSession = Depends(get_db)):
    items = await crud.get_items_by_host_id(db, host_id)
    return items


@router.post(
    '/',
    response_model=Item,
    status_code=status.HTTP_201_CREATED
)
async def add_item_to_db(item: CreateItem, db: AsyncSession = Depends(get_db)):
    return await crud.add_item(item=item, db=db)


@router.put('/', response_model=Item)
async def update_item(
        item: UpdateItemPartial,
        db: AsyncSession = Depends(get_db)
):
    db_item = await crud.get_item(db=db, item=item)
    if not db_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {item.name} not found")
    return await crud.update_item(db=db, db_item=db_item, item = item)


@router.patch('/', response_model=Item)
async def update_item_partial(
        item: UpdateItemPartial,
        db: AsyncSession = Depends(get_db)
):
    db_item = await crud.get_item(db=db, item=item)
    if not db_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item {item.name} not found")
    return await crud.update_item(db=db, db_item=db_item, item = item, partial=True)


@router.delete('/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_item_from_db(
        item: Item,
        db: AsyncSession = Depends(get_db),
):
    await crud.delete_item(db=db, host_id=item.host_id, name=item.name)

