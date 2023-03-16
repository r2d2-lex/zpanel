import logging
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from db import *
from schema import *
from Zabbix import *

logging.basicConfig(level=config.LOGGING_LEVEL)

db = Database()
db.fetch_by_query('users')

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/settings/")
def read_root():
    with ZabbixMonitoring() as zabbix_monitoring:
        hosts = zabbix_monitoring.get_all_hosts()
        return hosts


@app.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse("item.html", {"request": request, "id": id})


# @app.put("/items/{item_id}")
# def update_item(item_id: int, item: Item):
#     return {"item_name": item.name, "item_id": item_id}

# Получаем все хосты из Zabbix. Добавляем только те, которые мониторим в БД. + указываем в какой колонке
# они будут находиться
