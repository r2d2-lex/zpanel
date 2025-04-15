from fastapi import APIRouter
from fastapi import Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

import logging
import time

from auth.views import get_auth_user_username

logger = logging.getLogger(__name__)


from common import templates
from db import get_db
from AioZabbix import get_all_zabbix_monitoring_hosts
from items.views import get_item_by_host_id
from service import get_host_details
router = APIRouter(tags=['settings'])

@router.get('/settings', response_class=HTMLResponse)
async def ajax_settings(request: Request,
                        db: AsyncSession = Depends(get_db),
                        auth_username: str = Depends(get_auth_user_username),
                        ):
    time_start = time.time()
    template = 'zpanel/settings.html'
    zabbix_hosts = await get_all_zabbix_monitoring_hosts()
    monitoring_hosts = await get_host_details(zabbix_hosts, db)
    logger.info(f'Function SETTINGS delta time: {time.time() - time_start}. Username: \'{auth_username}\'')
    return templates.TemplateResponse(template,
                                      {
                                          'request': request,
                                          'hosts': monitoring_hosts,
                                      }
                                      )

@router.get('/', response_class=HTMLResponse)
def index(request: Request,
          auth_username: str = Depends(get_auth_user_username),
):
    return templates.TemplateResponse('zpanel/index.html',
                                      {
                                          'request': request,
                                          'page_title': 'Настройка',
                                          'username': auth_username,
                                      }
                                      )

@router.get('/data-items/{host_id}', response_class=HTMLResponse)
async def ajax_get_host_items(request: Request, host_items=Depends(get_item_by_host_id)):
    template = 'zpanel/items.html'
    return templates.TemplateResponse(template,
                                      {
                                          'request': request,
                                          'items': host_items,
                                      }
                                      )
