from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session
from json import JSONDecodeError
from pydantic.error_wrappers import ValidationError

from db import get_db
from schema import Host
from Zabbix import *
import config
import crud
import logging

COLUMN_FIELD = 'column'
PROBLEMS_FIELD = 'problems'

logging.basicConfig(level=config.LOGGING_LEVEL)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


async def get_schema_from_json_request(request: Request, schema_model):
    content_type = request.headers.get('content-type')
    logging.info(f'content_type: {content_type}')
    methods = ['POST', 'PUT', 'PATCH']

    if request.method in methods and 'application/json' in content_type:
        try:
            result_json = await request.json()
            if result_json:
                logging.debug(result_json)
                result = schema_model(**result_json)
                return result
        except JSONDecodeError:
            logging.error('encounter JSONDecodeError')
        except UnicodeDecodeError:
            logging.error('encounter UnicodeDecodeError')
        except ValidationError as err:
            logging.error(f'ValidationError {err}')
    logging.info('end request'.center(60, '*'))
    return


def update_monitoring_hosts(db, with_problems: bool = False) -> list:
    """ 
    Добавляет значение колонки (column) из БД в словарь мониторинга 
    Добавляет количество проблем (problems) в словарь мониторинга 
    """""
    monitoring_hosts = []
    zabbix_hosts = get_zabbix_monitoring_hosts()
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
    panel_hosts = []
    monitoring_hosts = update_monitoring_hosts(db, with_problems=True)
    for host in monitoring_hosts:
        try:
            if host[COLUMN_FIELD] > 0:
                panel_hosts.append(host)
        except KeyError:
            continue
    return templates.TemplateResponse('zpanel/panel.html',
                                      {
                                          'request': request,
                                          'hosts': panel_hosts,
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


@app.get('/settings/', response_class=HTMLResponse)
def settings(request: Request, db: Session = Depends(get_db)):
    template = 'zpanel/settings.html'
    monitoring_hosts = update_monitoring_hosts(db)
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


# Обработка запроса в ручную
# @app.post('/monitor/hosts/', response_model=Host)
# async def add_host_to_db(request: Request, db: Session = Depends(get_db)):
#     host = await get_schema_from_json_request(request, Host)
#     if host:
#         db_host = crud.get_host(db=db, hostid=host.hostid)
#         if db_host:
#             return  crud.update_host(db=db, host=host)
#             # raise HTTPException(status_code=400, detail="Host already monitored")
#         return crud.add_host(host=host, db=db)

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
    return get_zabbix_monitoring_hosts()


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
