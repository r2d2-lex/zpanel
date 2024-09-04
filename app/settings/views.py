from fastapi import APIRouter
from fastapi import Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

import time
import logging

from common import templates
from db import get_db
import AioZabbix
import items.views
import service
router = APIRouter(tags=['settings'])

@router.get('/settings', response_class=HTMLResponse)
async def ajax_settings(request: Request, db: AsyncSession = Depends(get_db)):
    time_start = time.time()
    template = 'zpanel/settings.html'
    zabbix_hosts = await AioZabbix.get_all_zabbix_monitoring_hosts()
    monitoring_hosts = await service.get_host_details(zabbix_hosts, db)
    logging.info(f'Function SETTINGS delta time: {time.time() - time_start}')
    return templates.TemplateResponse(template,
                                      {
                                          'request': request,
                                          'hosts': monitoring_hosts,
                                      }
                                      )

@router.get('/', response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse('zpanel/index.html',
                                      {
                                          'request': request,
                                          'page_title': 'Настройка',
                                      }
                                      )

@router.get('/data-items/{host_id}', response_class=HTMLResponse)
async def ajax_get_host_items(request: Request, host_items=Depends(items.views.get_item_by_host_id)):
    logging.info(f'host_items: {host_items}')
    for item in host_items:
        logging.info(f'item: {item.id} - {item.host_id} - {item.value_type} - {item.name}')
    template = 'zpanel/items.html'
    return templates.TemplateResponse(template,
                                      {
                                          'request': request,
                                          'items': host_items,
                                      }
                                      )
