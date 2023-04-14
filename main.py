from fastapi import FastAPI, Depends, Request, HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from db import get_db
from schema import Host, Item, HostId
from Zabbix import *
import config
import crud
import logging
import os

COLUMN_FIELD = 'column'
PROBLEMS_FIELD = 'problems'
IMAGE_FIELD = 'image'
DATA_ITEMS_FIELD = 'data_items'
# from upload.js:
IMAGE_HOST_ID_FIELD = 'host-id'

logging.basicConfig(level=config.LOGGING_LEVEL)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
CURRENT_WORK_DIRECTORY = os.getcwd()
CURRENT_IMAGES_DIRECTORY = CURRENT_WORK_DIRECTORY + '/static/images/'


def get_monitored_hosts_ids(db) -> list:
    host_ids = []
    db_hosts = crud.get_monitored_hosts(db)
    for db_host in db_hosts:
        if db_host.column > 0:
            host_ids.append(db_host.hostid)
    return host_ids


def get_data_items(db, host_id) -> list:
    result = []
    data_items = crud.get_items(db, host_id)
    for item in data_items:
        items_result = get_host_item_value(host_id, item.name)
        if items_result:
            result.append({'item_value': items_result, 'item_type': item.value_type})
    return result


def update_monitoring_hosts(zabbix_hosts, db, with_problems: bool = False) -> list:
    """ 
    Добавляет значение колонки (column) из БД в словарь мониторинга 
    Добавляет количество проблем (problems) в словарь мониторинга 
    Добавляет имя файла изображения (image) в словарь мониторинга 
    """""
    monitoring_hosts = []
    db_hosts = crud.get_monitored_hosts(db)

    for zabbix_host in zabbix_hosts:
        image = ''
        problems = []
        column = 0
        items = []
        for db_host in db_hosts:
            try:
                if int(zabbix_host[HOST_ID_FIELD]) == int(db_host.hostid):
                    items = get_data_items(db, db_host.hostid)

                    if db_host.image:
                        image = db_host.image

                    if with_problems:
                        problems = get_zabbix_host_problems(db_host.hostid)
                    logging.debug('{host} in database'.format(host=db_host.hostid))
                    column = db_host.column
                    break
            except KeyError as error:
                logging.error(f'KeyError: {error}')

        view_host = dict()
        view_host.update(zabbix_host)
        view_host.update({COLUMN_FIELD: column})
        if image:
            view_host.update({IMAGE_FIELD: image})
        if with_problems:
            view_host.update({PROBLEMS_FIELD: problems})
        if items:
            view_host.update({DATA_ITEMS_FIELD: items})

        monitoring_hosts.append(view_host)
    # Финальная сортировка списка по Имени(NAME_FIELD) машины
    monitoring_hosts = sorted(monitoring_hosts, key=lambda x: x[NAME_FIELD])
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
def monitoring_panel(request: Request, db: Session = Depends(get_db)):
    template = 'zpanel/panel.html'
    host_ids = get_monitored_hosts_ids(db)
    zabbix_hosts = get_zabbix_monitoring_hosts(host_ids)
    monitoring_hosts = update_monitoring_hosts(zabbix_hosts, db, with_problems=True)
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


# Эта функция - костыль. Иначе изображение не загружается корректно. Связано с асинхронностью выполнения
async def parse_host_id(request):
    host_id = 0
    form_data = await request.form()
    form_data = jsonable_encoder(form_data)
    try:
        host_id = form_data[IMAGE_HOST_ID_FIELD]
    except KeyError as error:
        logging.error(f'Ошибка получения host_id: {error}')
    return int(host_id)


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
async def upload_image(image: UploadFile, request: Request, db: Session = Depends(get_db)):
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

    db_host = crud.get_host(db=db, hostid=host_id)
    if db_host:
        logging.info(f'Image name: {image_name}')
        crud.update_host_image(db=db, host=db_host, image_name=str(image_name))
    else:
        return {'error': 'Ошибка БД', }
    return {'error': '', 'success': image_name, }


@app.get('/settings/', response_class=HTMLResponse)
def settings(request: Request, db: Session = Depends(get_db)):
    template = 'zpanel/settings.html'
    zabbix_hosts = get_all_zabbix_monitoring_hosts()
    monitoring_hosts = update_monitoring_hosts(zabbix_hosts, db)
    return templates.TemplateResponse(template,
                                      {
                                          'request': request,
                                          'hosts': monitoring_hosts,
                                      }
                                      )


# Хосты, которые будут мониторится
@app.get('/monitor/hosts/', response_model=list[Host])
async def read_host_from_db(db: Session = Depends(get_db)):
    hosts = crud.get_monitored_hosts(db)
    return hosts


@app.post('/monitor/hosts/', response_model=Host)
def add_host_to_db(host: Host, db: Session = Depends(get_db)):
    db_host = crud.get_host(db=db, hostid=host.hostid)
    if db_host:
        # raise HTTPException(status_code=400, detail="Host already monitored")
        return crud.update_host(db=db, host=host)
    return crud.add_host(host=host, db=db)


@app.delete('/monitor/hosts/', response_model=Host)
def delete_host_from_db(host: Host, db: Session = Depends(get_db)):
    db_host = crud.get_host(db=db, hostid=host.hostid)
    if not db_host:
        raise HTTPException(status_code=400, detail="Host not found")
    return crud.delete_host(db=db, hostid=host.hostid)


@app.patch('/monitor/hosts/', response_model=Host)
def update_host_from_db(host: Host, db: Session = Depends(get_db)):
    db_host = crud.get_host(db=db, hostid=host.hostid)
    if not db_host:
        raise HTTPException(status_code=400, detail="Host not found")
    return crud.update_host(db=db, host=host)


@app.get('/hosts')
def get_all_hosts():
    return get_all_zabbix_monitoring_hosts()


@app.post('/errors/', response_class=HTMLResponse)
def get_host_errors(request: Request, host: Host):
    host_problems = get_zabbix_host_problems(host.hostid)
    template = 'zpanel/problems.html'
    return templates.TemplateResponse(template,
                                      {
                                          'request': request,
                                          'problems': host_problems,
                                      }
                                      )


@app.post('/data-items/', response_class=HTMLResponse)
def get_host_items(request: Request, host_id: HostId, db: Session = Depends(get_db)):
    host_items = crud.get_items(db, host_id.host_id)
    template = 'zpanel/items.html'
    return templates.TemplateResponse(template,
                                      {
                                          'request': request,
                                          'items': host_items,
                                      }
                                      )


# -------------------------- ( Item ) -----------------------
@app.get('/items/', response_model=list[Item])
async def get_item_from_db(host_id: int, db: Session = Depends(get_db)):
    items = crud.get_items(db, host_id)
    return items


@app.post('/items/', response_model=Item)
async def add_item_to_db(item: Item, db: Session = Depends(get_db)):
    db_item = crud.get_item(db=db, item=item)
    if db_item:
        raise HTTPException(status_code=400, detail="Item already exist")
    return crud.add_item(item=item, db=db)


@app.delete('/items/', response_model=Item)
async def delete_item_from_db(item: Item, db: Session = Depends(get_db)):
    db_item = crud.get_item(db=db, item=item)
    if not db_item:
        raise HTTPException(status_code=400, detail="Item not found")
    return crud.delete_item(db=db, host_id=item.host_id, name=item.name)


@app.patch('/items/', response_model=Item)
async def update_item(item: Item, db: Session = Depends(get_db)):
    db_item = crud.get_item(db=db, item=item)
    if not db_item:
        raise HTTPException(status_code=400, detail="Item not found")
    return crud.update_item(db=db, item=item)
