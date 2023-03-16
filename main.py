import logging
from fastapi import FastAPI
from db import *
from schema import *

logging.basicConfig(level=config.LOGGING_LEVEL)

db = Database()
db.fetch_by_query('users')

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}

# Получаем все хосты из Zabbix. Добавляем только те, которые мониторим в БД. + указываем в какой колонке
# они будут находиться
