from fastapi import FastAPI, Depends, Request, HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from db import get_db
from schema import Host
from Zabbix import *
import config
import crud
import logging
import os

COLUMN_FIELD = 'column'
PROBLEMS_FIELD = 'problems'
# from upload.js:
IMAGE_HOST_ID_FIELD = 'host-id'

logging.basicConfig(level=config.LOGGING_LEVEL)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def get_monitored_hosts_ids(db) -> list:
    host_ids = []
    db_hosts = crud.get_monitored_hosts(db)
    for db_host in db_hosts:
        if db_host.column > 0:
            host_ids.append(db_host.hostid)
    return host_ids


def update_monitoring_hosts(zabbix_hosts, db, with_problems: bool = False) -> list:
    """ 
    Добавляет значение колонки (column) из БД в словарь мониторинга 
    Добавляет количество проблем (problems) в словарь мониторинга 
    """""
    monitoring_hosts = []
    db_hosts = crud.get_monitored_hosts(db)

    for zabbix_host in zabbix_hosts:
        problems = []
        column = 0
        for db_host in db_hosts:
            try:
                if int(zabbix_host[HOST_ID_FIELD]) == int(db_host.hostid):
                    if with_problems:
                        problems = get_zabbix_host_problems(db_host.hostid)
                    logging.debug('{host} in database'.format(host=db_host.hostid))
                    column = db_host.column
            except KeyError as error:
                logging.error(f'KeyError: {error}')

        view_host = dict()
        view_host.update(zabbix_host)
        view_host.update({COLUMN_FIELD: column})
        if with_problems:
            view_host.update({PROBLEMS_FIELD: problems})

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
async def download_image(image_name: str, db: Session = Depends(get_db)):
    result = ''
    file_path = os.getcwd() + '/images/' + image_name
    logging.info(f'File path: {file_path}')
    try:
        result = FileResponse(path=file_path, filename=image_name)
    except RuntimeError as error:
        logging.error(f'Невозможно загрузить файл {error}')
    return result


@app.post('/upload/')
async def upload_image(image: UploadFile, request: Request, db: Session = Depends(get_db)):
    cwd = os.getcwd()
    logging.info(f'Current work directory {cwd}')

    image_name = image.filename
    image_path = cwd + '/images/' + image_name
    logging.info(f'Image full path: {image_path}')

    try:
        image_content = image.file.read()
        with open(image_path, "wb") as f:
            f.write(image_content)
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        image.file.close()

    host_id = await parse_host_id(request)
    logging.info(f'Load image for Host ID: {host_id}')

    # db_host = crud.get_host(db=db, hostid=host_id)
    # if db_host:
    #     crud.update_host(db=db, host=db_host.)
    return {'message': image.filename}


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
