# import logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from db import *
from schema import *
from Zabbix import *

logging.basicConfig(level=config.LOGGING_LEVEL)

with Database() as db:
    db.fetch_by_query('hosts')

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
@app.get('/monitor/hosts/')
async def read_item():
    with Database() as database:
        result = database.get_host()
    return result


# Хост, который добавим в таблицу
@app.put('/monitor/hosts/{host_id}', response_model=Host)
async def update_host(host: Host):
    update_item_encoded = jsonable_encoder(host)
    with Database() as database:
        result = database.add_host()
    print(f'result: {result}')
    return result


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
