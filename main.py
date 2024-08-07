import uvicorn
from fastapi import FastAPI, Depends, Request, HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_db
from schema import Host, Item
from AioZabbix import HOST_ID_FIELD, NAME_FIELD
from AioZabbix import AioZabbixApi, async_get_zabbix_host_problems, async_get_host_problems, \
    async_get_all_zabbix_monitoring_hosts, async_get_zabbix_monitoring_hosts
import asyncio
import config
import crud
import logging
import os
import time

COLUMN_FIELD = 'column'
PROBLEMS_FIELD = 'problems'
IMAGE_FIELD = 'image'
DATA_ITEMS_FIELD = 'data_items'
# from upload.js:
IMAGE_HOST_ID_FIELD = 'host-id'

logging.basicConfig(level=config.LOGGING_LEVEL)

app = FastAPI()

if config.ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
CURRENT_WORK_DIRECTORY = os.getcwd()
CURRENT_IMAGES_DIRECTORY = CURRENT_WORK_DIRECTORY + '/static/images/'


async def get_monitored_hosts_ids(db: AsyncSession) -> list:
    db_hosts = await crud.get_monitored_hosts(db)
    return [db_host.host_id for db_host in db_hosts if db_host.column > 0]


async def get_data_items(db: AsyncSession, api: AioZabbixApi, host_id: int) -> list:
    result = []
    data_items = await crud.get_items(db, host_id)
    for item in data_items:
        items_result = await api.async_get_host_item_value([host_id], item.name)
        logging.debug(f'Data_Item for Host_id: {host_id} item name: {item.name} item result: {items_result}')
        if items_result:
            result.append({'item_value': items_result, 'item_type': item.value_type})
        else:
            result.append({'item_value': 'None', 'item_type': item.value_type})
    return result


async def get_async_host_details(api: AioZabbixApi,
                                 zabbix_host: dict,
                                 db: AsyncSession,
                                 monitoring_hosts: list,
                                 with_problems: bool):
    """
        api - context aio_zabbix_api для запроса;
        zabbix_hosts - список словарей всех хостов из api zabbix
        db - контекст БД
        monitoring_hosts - словарь, который будет выведен на панель мониторинга

        Добавляет значение колонки (column) из БД в словарь мониторинга
        Добавляет количество проблем (problems) в словарь мониторинга
        Добавляет имя файла изображения (image) в словарь мониторинга
        Добавляет элементы данных (data_items) в словарь мониторинга
    """
    await asyncio.sleep(0)
    column = 0
    try:
        host_id = int(zabbix_host[HOST_ID_FIELD])
    except KeyError as error:
        logging.info(f'Ошибка ключа {HOST_ID_FIELD} элемента списка zabbix: {error}')
        return

    view_host = dict()
    view_host.update(zabbix_host)

    db_host = await crud.get_host(db, host_id)
    if db_host:
        items = await get_data_items(db, api, host_id)
        if items:
            view_host.update({DATA_ITEMS_FIELD: items})
        if db_host.image:
            view_host.update({IMAGE_FIELD: db_host.image})
        column = db_host.column if db_host.column else 0

        if with_problems:
            view_host.update({PROBLEMS_FIELD: await async_get_zabbix_host_problems(api, host_id)})

    view_host.update({COLUMN_FIELD: column})
    monitoring_hosts.append(view_host)
    return


async def get_host_details(zabbix_hosts: list, db: AsyncSession = Depends(get_db), with_problems: bool = False) -> list:
    monitoring_hosts = []
    try:
        async with AioZabbixApi() as aio_zabbix:
            futures = [asyncio.ensure_future(
                get_async_host_details(aio_zabbix, host, db, monitoring_hosts, with_problems)) for host in zabbix_hosts]
            await asyncio.wait(futures)
    except ValueError as error:
        logging.info(f'Set of coroutines/Futures is empty. Error: {error}')

    # сортировка списка по Имени(NAME_FIELD) машины
    monitoring_hosts = sorted(monitoring_hosts, key=lambda x: x[NAME_FIELD])
    if with_problems:
        # Финальная сортировка списка по кол-ву проблем (PROBLEMS_FIELD) элемента
        monitoring_hosts = sorted(monitoring_hosts, reverse=True, key=lambda x: len(x[PROBLEMS_FIELD]))

    return monitoring_hosts


@app.get('/monitoring/', response_class=HTMLResponse)
def monitoring(request: Request):
    return templates.TemplateResponse('zpanel/monitoring.html',
                                      {
                                          'request': request,
                                          'page_title': 'Мониторинг',
                                      }
                                      )


@app.get('/panel/', response_class=HTMLResponse)
async def monitoring_panel(request: Request, db: AsyncSession = Depends(get_db)):
    time_start = time.time()
    template = 'zpanel/panel.html'
    host_ids = await get_monitored_hosts_ids(db)
    zabbix_hosts = await async_get_zabbix_monitoring_hosts(host_ids)
    monitoring_hosts = await get_host_details(zabbix_hosts, db, with_problems=True)
    logging.info(f'Function PANEL delta time: {time.time() - time_start}')
    return templates.TemplateResponse(template,
                                      {
                                          'request': request,
                                          'hosts': monitoring_hosts,
                                      }
                                      )


@app.get('/', response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse('zpanel/index.html',
                                      {
                                          'request': request,
                                          'page_title': 'Настройка',
                                      }
                                      )


async def parse_host_id(request: Request) -> int:
    host_id = 0
    form_data = await request.form()
    form_data = jsonable_encoder(form_data)
    try:
        host_id = int(form_data[IMAGE_HOST_ID_FIELD])
    except (KeyError, ValueError) as error:
        logging.error(f'Ошибка получения host_id: {error}')
    return host_id


@app.get('/images/{image_name}')
async def download_image(image_name: str):
    result = ''
    file_path = CURRENT_IMAGES_DIRECTORY + image_name
    logging.info(f'File path: {file_path}')
    try:
        result = FileResponse(path=file_path, filename=image_name)
    except RuntimeError as error:
        logging.error(f'Невозможно загрузить файл {error}')
    return result


@app.post('/upload/')
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

    db_host = await crud.get_host(db=db, host_id=host_id)
    if db_host:
        logging.info(f'Image name: {image_name}')
        await crud.update_host_image(db=db, host=db_host, image_name=str(image_name))
    else:
        return {'error': 'Ошибка БД', }
    return {'error': '', 'success': image_name, }


@app.get('/hosts')
async def get_all_hosts():
    return await async_get_all_zabbix_monitoring_hosts()


@app.get('/settings/', response_class=HTMLResponse)
async def settings(request: Request, db: AsyncSession = Depends(get_db)):
    time_start = time.time()
    template = 'zpanel/settings.html'
    zabbix_hosts = await async_get_all_zabbix_monitoring_hosts()
    monitoring_hosts = await get_host_details(zabbix_hosts, db)
    logging.info(f'Function SETTINGS delta time: {time.time() - time_start}')
    return templates.TemplateResponse(template,
                                      {
                                          'request': request,
                                          'hosts': monitoring_hosts,
                                      }
                                      )


# Хосты, которые будут мониторится
@app.get('/monitor/hosts/', response_model=list[Host])
async def read_host_from_db(db: AsyncSession = Depends(get_db)):
    hosts = await crud.get_monitored_hosts(db)
    return hosts


@app.get('/monitor/hosts/{host_id}', response_model=Host)
async def get_host_from_db(host_id: int, db: AsyncSession = Depends(get_db)):
    db_host = await crud.get_host(db=db, host_id=host_id)
    if not db_host:
        raise HTTPException(status_code=404, detail="Host not found")
    return db_host


@app.post('/monitor/hosts/', response_model=Host)
async def add_host_to_db(host: Host, db: AsyncSession = Depends(get_db)):
    db_host = await crud.get_host(db=db, host_id=host.host_id)
    if db_host:
        return await crud.update_host(db=db, host=host)
    return await crud.add_host(host=host, db=db)


@app.delete('/monitor/hosts/', response_model=Host)
async def delete_host_from_db(host: Host, db: AsyncSession = Depends(get_db)):
    db_host = await crud.get_host(db=db, host_id=host.host_id)
    if not db_host:
        raise HTTPException(status_code=400, detail="Host not found")
    return await crud.delete_host(db=db, host_id=host.host_id)


@app.patch('/monitor/hosts/', response_model=Host)
async def update_host_from_db(host: Host, db: AsyncSession = Depends(get_db)):
    db_host = await crud.get_host(db=db, host_id=host.host_id)
    if not db_host:
        raise HTTPException(status_code=400, detail="Host not found")
    return await crud.update_host(db=db, host=host)


@app.get('/errors/{host_id}', response_class=HTMLResponse)
async def get_host_errors(request: Request, host_id: int):
    host_problems = await async_get_host_problems(host_id)
    template = 'zpanel/problems.html'
    return templates.TemplateResponse(template,
                                      {
                                          'request': request,
                                          'problems': host_problems,
                                      }
                                      )


# -------------------------- ( Item ) -----------------------
@app.get('/items/{host_id}', response_model=list[Item])
async def get_item_from_db(host_id: int, db: AsyncSession = Depends(get_db)):
    items = await crud.get_items(db, host_id)
    return items


@app.get('/data-items/{host_id}', response_class=HTMLResponse)
async def get_host_items(request: Request, host_items=Depends(get_item_from_db)):
    template = 'zpanel/items.html'
    return templates.TemplateResponse(template,
                                      {
                                          'request': request,
                                          'items': host_items,
                                      }
                                      )


@app.post('/items/', response_model=Item)
async def add_item_to_db(item: Item, db: AsyncSession = Depends(get_db)):
    db_item = await crud.get_item(db=db, item=item)
    if db_item:
        raise HTTPException(status_code=400, detail="Item already exist")
    return await crud.add_item(item=item, db=db)


@app.delete('/items/', response_model=Item)
async def delete_item_from_db(item: Item, db: AsyncSession = Depends(get_db)):
    db_item = await crud.get_item(db=db, item=item)
    if not db_item:
        raise HTTPException(status_code=400, detail="Item not found")
    return await crud.delete_item(db=db, host_id=item.host_id, name=item.name)


@app.patch('/items/', response_model=Item)
async def update_item(item: Item, db: AsyncSession = Depends(get_db)):
    db_item = await crud.get_item(db=db, item=item)
    if not db_item:
        raise HTTPException(status_code=400, detail="Item not found")
    return await crud.update_item(db=db, item=item)


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
