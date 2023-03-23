from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session
from json import JSONDecodeError

from db import get_db
from schema import Host
from Zabbix import *
import config
import crud
import logging

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
    logging.info('end request'.center(60, '*'))
    return


@app.get('/', response_class=HTMLResponse)
def index(request: Request):
    hosts = get_zabbix_monitoring_hosts()
    return templates.TemplateResponse('zpanel/index.html',
                                      {
                                          'request': request,
                                          'page_title': 'Настройка',
                                          'hosts': hosts,
                                      }
                                      )


# Хосты, которые будут мониторится
@app.get('/monitor/hosts/', response_model=list[Host])
async def read_host_from_db(db: Session = Depends(get_db)):
    hosts = crud.get_monitored_hosts(db)
    return hosts


# Хост, который добавим в таблицу
@app.post('/monitor/hosts/', response_model=Host)
async def add_host_to_db(request: Request, db: Session = Depends(get_db)):
    host = await get_schema_from_json_request(request, Host)
    if host:
        db_host = crud.get_host(db=db, hostid=host.hostid)
        if db_host:
            return  crud.update_host(db=db, host=host)
            # raise HTTPException(status_code=400, detail="Host already monitored")
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


@app.get('/errors/')
def get_host_errors(host_id: int):
    return get_zabbix_host_problems(host_id)


@app.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse("item.html", {"request": request, "id": id})

# Получаем все хосты из Zabbix. Добавляем только те, которые мониторим в БД. + указываем в какой колонке
# они будут находиться
