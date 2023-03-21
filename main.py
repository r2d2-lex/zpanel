# import logging
from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from db import SessionLocal, engine
from schema import *
from Zabbix import *
import crud

logging.basicConfig(level=config.LOGGING_LEVEL)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
    hosts = crud.get_hosts(db)
    return hosts


# Хост, который добавим в таблицу
@app.post('/monitor/hosts/', response_model=Host)
def create_host(host: Host, db: Session = Depends(get_db)):
    return crud.add_host(host=host, db=db)


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
