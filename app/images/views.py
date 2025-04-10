from fastapi import APIRouter, UploadFile, HTTPException
from fastapi import Depends, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

import logging
logger = logging.getLogger(__name__)

import os

from db import get_db
from hosts.crud import get_host, update_host_image

router = APIRouter(tags=['images'], prefix='/image')

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
        logger.error(f'Ошибка получения host_id: {error}')
    return host_id


@router.get('/{image_name}')
async def show_image(image_name: str):
    file_path = os.path.join(CURRENT_IMAGES_DIRECTORY, image_name)

    logger.info(f'File path: {file_path}')
    if not os.path.isfile(file_path):
        logger.error(f'Файл не найден: {file_path}')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Файл не найден")

    try:
        return FileResponse(path=file_path, filename=image_name)
    except Exception as error:
        logger.error(f'Ошибка при загрузке файла: {error}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка при загрузке файла")


@router.post('/upload')
async def upload_image(
        image: UploadFile,
        request: Request,
        db: AsyncSession = Depends(get_db)
):
    logger.info(f'Current work directory {CURRENT_WORK_DIRECTORY}')
    image_name = image.filename
    image_path = os.path.join(CURRENT_IMAGES_DIRECTORY, image_name)
    logger.info(f'Image full path: {image_path}')

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
    logger.info(f'Load image for Host ID: {host_id}')

    db_host = await get_host(db=db, host_id=host_id)
    if db_host:
        logger.info(f'Image name: {image_name}')
        await update_host_image(db=db, host=db_host, image_name=str(image_name))
    else:
        return {'error': 'Ошибка БД', }
    return {'error': '', 'success': image_name, }
