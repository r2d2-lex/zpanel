from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from db import get_db
from schema import *
from Zabbix import *
import crud

logging.basicConfig(level=config.LOGGING_LEVEL)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get('/', response_class=HTMLResponse)
def index(request: Request):
    with ZabbixMonitoring() as zabbix_monitoring:
        hosts = zabbix_monitoring.get_all_hosts()
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
import logging
from json import JSONDecodeError
@app.post('/monitor/hosts/')
async def test(req: Request):
    content_type = req.headers.get('content-type')
    print(content_type)
    methods = ['POST', 'PUT', 'PATCH']

    if req.method in methods and 'application/json' in content_type:
        try:
            params = await req.json()
            if params:
                logging.info(params)
        except JSONDecodeError:
            logging.error('encounter JSONDecodeError')
        except UnicodeDecodeError:
            logging.error('encounter UnicodeDecodeError')
    logging.info('end request'.center(60, '*'))
    return


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
    with ZabbixMonitoring() as zabbix_monitoring:
        return zabbix_monitoring.get_all_hosts()


@app.get('/errors/')
def get_host_errors(host_id: int):
    with ZabbixMonitoring() as zabbix_monitoring:
        result = zabbix_monitoring.get_host_problem(host_id)
        return result


@app.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse("item.html", {"request": request, "id": id})

# Получаем все хосты из Zabbix. Добавляем только те, которые мониторим в БД. + указываем в какой колонке
# они будут находиться
