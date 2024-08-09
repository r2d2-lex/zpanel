from fastapi import APIRouter, UploadFile
from fastapi import Depends, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

import os
import logging

from app.db import get_db
from app.hosts.crud import get_host, update_host_image

router = APIRouter(tags=['images'])

# from upload.js:
IMAGE_HOST_ID_FIELD = 'host-id'

CURRENT_WORK_DIRECTORY = os.getcwd()
CURRENT_IMAGES_DIRECTORY = CURRENT_WORK_DIRECTORY + '/static/images/'

async def parse_host_id(request: Request) -> int:
    host_id = 0
    form_data = await request.form()
    form_data = jsonable_encoder(form_data)
    try:
        host_id = int(form_data[IMAGE_HOST_ID_FIELD])
    except (KeyError, ValueError) as error:
        logging.error(f'Ошибка получения host_id: {error}')
    return host_id


@router.get('/images/{image_name}')
async def show_image(image_name: str):
    result = ''
    file_path = CURRENT_IMAGES_DIRECTORY + image_name
    logging.info(f'File path: {file_path}')
    try:
        result = FileResponse(path=file_path, filename=image_name)
    except RuntimeError as error:
        logging.error(f'Невозможно загрузить файл {error}')
    return result


@router.post('/upload/')
async def upload_image(image: UploadFile, request: Request, db: AsyncSession = Depends(get_db)):
    logging.info(f'Current work directory {CURRENT_WORK_DIRECTORY}')
    image_name = image.filename
    image_path = CURRENT_IMAGES_DIRECTORY + image_name
    logging.info(f'Image full path: {image_path}')

    try:
        image_content = image.file.read()
        with open(image_path, "wb") as f:
            f.write(image_content)
    except Exception as error:
        return {'error': error, }
    finally:
        image.file.close()

    host_id = await parse_host_id(request)
    if not host_id:
        return {'error': 'Невозможно получить host_id', }
    logging.info(f'Load image for Host ID: {host_id}')

    db_host = await get_host(db=db, host_id=host_id)
    if db_host:
        logging.info(f'Image name: {image_name}')
        await update_host_image(db=db, host=db_host, image_name=str(image_name))
    else:
        return {'error': 'Ошибка БД', }
    return {'error': '', 'success': image_name, }
