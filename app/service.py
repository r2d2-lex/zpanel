import asyncio
import logging
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from exceptions import BadRequestFromApi

logger = logging.getLogger(__name__)

from AioZabbix import HOST_ID_FIELD, NAME_FIELD
from AioZabbix import AioZabbixApi, get_zabbix_host_problems
from hosts.crud import get_host
from items.crud import get_items_by_host_id
from db import get_db

COLUMN_FIELD = 'column'
PROBLEMS_FIELD = 'problems'
IMAGE_FIELD = 'image'
DATA_ITEMS_FIELD = 'data_items'


async def get_data_items(db: AsyncSession, api: AioZabbixApi, host_id: int) -> list:
    result = []
    data_items = await get_items_by_host_id(db, host_id)
    for item in data_items:
        items_result = await api.get_host_item_value([host_id], item.name)
        logger.debug(f'Data_Item for Host_id: {host_id} item name: {item.name} item result: {items_result}')
        if items_result:
            result.append({'item_value': items_result, 'item_type': item.value_type})
        else:
            result.append({'item_value': 'None', 'item_type': item.value_type})
    return result


async def get_async_host_details(api: AioZabbixApi,
                                 zabbix_host: dict,
                                 db: AsyncSession,
                                 monitoring_hosts: list,
                                 api_problems: list,
                                 with_problems: bool):
    """
        api - context aio_zabbix_api для запроса;
        zabbix_hosts - список словарей всех хостов из api zabbix
        db - контекст БД
        monitoring_hosts - список хостов(словарь), который будет выведен на панель мониторинга
        api_problems - список строк о ошибках при выхове api

        Добавляет значение колонки (column) из БД в словарь мониторинга
        Добавляет количество проблем (problems) в словарь мониторинга
        Добавляет имя файла изображения (image) в словарь мониторинга
        Добавляет элементы данных (data_items) в словарь мониторинга
    """
    await asyncio.sleep(0)
    column = 0
    # Мы хотим показать информацию по всем возможным хостам в панели поэтому мы именно здесь ловим исключение BadRequestFromApi
    try:
        try:
            host_id = int(zabbix_host[HOST_ID_FIELD])
        except KeyError as error:
            error_message = 'Ошибка ключа %s элемента списка zabbix: %s' % (HOST_ID_FIELD, error)
            logger.exception(error_message)
            api_problems.append(error_message)
            return

        view_host = dict()
        view_host.update(zabbix_host)

        db_host = await get_host(db, host_id)
        if db_host:
            items = await get_data_items(db, api, host_id)
            if items:
                view_host.update({DATA_ITEMS_FIELD: items})
            if db_host.image:
                view_host.update({IMAGE_FIELD: db_host.image})
            column = db_host.column if db_host.column else 0

            if with_problems:
                view_host.update({PROBLEMS_FIELD: await get_zabbix_host_problems(api, host_id)})

        view_host.update({COLUMN_FIELD: column})
        monitoring_hosts.append(view_host)

    except BadRequestFromApi as request_error:
        logger.info(request_error)
        api_problems.append(request_error)
    return


async def get_host_details(zabbix_hosts: list, db: AsyncSession = Depends(get_db), with_problems: bool = False) -> tuple[list, list]:
    monitoring_hosts = []
    api_problems = []
    try:
        async with AioZabbixApi() as aio_zabbix:
            futures = [asyncio.ensure_future(
                get_async_host_details(aio_zabbix, host, db, monitoring_hosts, api_problems, with_problems)) for host in zabbix_hosts]
            await asyncio.wait(futures)
    except ValueError as error:
        logger.exception(f'Set of coroutines/Futures is empty. Error: {error}')

    # сортировка списка по Имени(NAME_FIELD) машины
    monitoring_hosts = sorted(monitoring_hosts, key=lambda x: x[NAME_FIELD])
    if with_problems:
        # Финальная сортировка списка по кол-ву проблем (PROBLEMS_FIELD) элемента
        monitoring_hosts = sorted(monitoring_hosts, reverse=True, key=lambda x: len(x[PROBLEMS_FIELD]))

    return monitoring_hosts, api_problems
