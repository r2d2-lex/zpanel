from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import items.crud as crud
from items.schema import Item
from db import get_db

router = APIRouter(prefix='/items', tags=['items'])

@router.get('/{host_id}', response_model=list[Item])
async def get_item_from_db(host_id: int, db: AsyncSession = Depends(get_db)):
    items = await crud.get_items(db, host_id)
    return items


@router.post('/', response_model=Item)
async def add_item_to_db(item: Item, db: AsyncSession = Depends(get_db)):
    db_item = await crud.get_item(db=db, item=item)
    if db_item:
        raise HTTPException(status_code=400, detail="Item already exist")
    return await crud.add_item(item=item, db=db)


@router.delete('/', response_model=Item)
async def delete_item_from_db(item: Item, db: AsyncSession = Depends(get_db)):
    db_item = await crud.get_item(db=db, item=item)
    if not db_item:
        raise HTTPException(status_code=400, detail="Item not found")
    return await crud.delete_item(db=db, host_id=item.host_id, name=item.name)


@router.patch('/', response_model=Item)
async def update_item(item: Item, db: AsyncSession = Depends(get_db)):
    db_item = await crud.get_item(db=db, item=item)
    if not db_item:
        raise HTTPException(status_code=400, detail="Item not found")
    return await crud.update_item(db=db, item=item)
