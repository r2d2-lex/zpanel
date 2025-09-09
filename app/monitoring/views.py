from pprint import pprint

from fastapi import APIRouter
from fastapi import Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from AioZabbix import get_zabbix_monitoring_hosts, get_host_problems
from common import templates

import time
import logging

from db import get_db
from exceptions import BadResponseFromApi
from hosts.crud import get_monitored_hosts
from service import get_host_details

logger = logging.getLogger(__name__)
router = APIRouter(tags=['monitoring'])


async def get_monitored_hosts_ids(db: AsyncSession) -> list:
    """Получаем список ИД-шников хостов, которые мониторятся в Zabbix + будут добавлены в мониторинг панели"""
    db_hosts = await get_monitored_hosts(db)
    return [db_host.host_id for db_host in db_hosts if db_host.column > 0]


@router.get('/monitoring', response_class=HTMLResponse)
def monitoring(request: Request):
    return templates.TemplateResponse('/zpanel/monitoring.html',
                                      {
                                          'request': request,
                                          'page_title': 'Мониторинг',
                                      }
                                      )


@router.get('/panel/', response_class=HTMLResponse)
async def ajax_monitoring_panel(request: Request, db: AsyncSession = Depends(get_db)):
    zabbix_monitoring_hosts_problems = []
    zabbix_hosts = []
    time_start = time.time()
    template = 'zpanel/panel.html'
    host_ids = await get_monitored_hosts_ids(db)
    try:
        zabbix_hosts = await get_zabbix_monitoring_hosts(host_ids)
    except BadResponseFromApi as error_api:
        logger.exception(error_api)
        zabbix_monitoring_hosts_problems.append(error_api)

    monitoring_hosts, api_problems = await get_host_details(zabbix_hosts, db, with_problems=True)
    if len(host_ids) != len(monitoring_hosts):
        message = 'Данные в БД не совпадают с полученными данными из Api'
        logger.info(message)
        zabbix_monitoring_hosts_problems.append(message)

    if zabbix_monitoring_hosts_problems:
        api_problems = zabbix_monitoring_hosts_problems + api_problems
    logger.info(f'Function PANEL delta time: {time.time() - time_start}')
    return templates.TemplateResponse(template,
                                      {
                                          'request': request,
                                          'hosts': monitoring_hosts,
                                          'problems': api_problems,
                                      }
                                      )


@router.get('/errors/{host_id}', response_class=HTMLResponse)
async def ajax_get_host_errors(request: Request, host_id: int):
    host_problems = await get_host_problems(host_id)
    template = 'zpanel/problems.html'
    return templates.TemplateResponse(template,
                                      {
                                          'request': request,
                                          'problems': host_problems,
                                      }
                                      )
