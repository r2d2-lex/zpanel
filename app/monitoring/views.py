from fastapi import APIRouter
from fastapi import Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.AioZabbix import async_get_zabbix_monitoring_hosts, async_get_host_problems
from app.common import templates

import time
import logging

from app.db import get_db
from app.hosts.crud import get_monitored_hosts
from app.items.views import get_item_from_db
from app.service import get_host_details

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
    time_start = time.time()
    template = 'zpanel/panel.html'
    host_ids = await get_monitored_hosts_ids(db)
    zabbix_hosts = await async_get_zabbix_monitoring_hosts(host_ids)
    monitoring_hosts = await get_host_details(zabbix_hosts, db, with_problems=True)
    logging.info(f'Function PANEL delta time: {time.time() - time_start}')
    return templates.TemplateResponse(template,
                                      {
                                          'request': request,
                                          'hosts': monitoring_hosts,
                                      }
                                      )


@router.get('/errors/{host_id}', response_class=HTMLResponse)
async def ajax_get_host_errors(request: Request, host_id: int):
    host_problems = await async_get_host_problems(host_id)
    template = 'zpanel/problems.html'
    return templates.TemplateResponse(template,
                                      {
                                          'request': request,
                                          'problems': host_problems,
                                      }
                                      )


@router.get('/data-items/{host_id}', response_class=HTMLResponse)
async def ajax_get_host_items(request: Request, host_items=Depends(get_item_from_db)):
    template = 'zpanel/items.html'
    return templates.TemplateResponse(template,
                                      {
                                          'request': request,
                                          'items': host_items,
                                      }
                                      )
