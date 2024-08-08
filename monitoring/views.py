from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix='/monitoring')


@router.get('/', response_class=HTMLResponse)
def monitoring(request: Request):
    return templates.TemplateResponse('/zpanel/monitoring.html',
                                      {
                                          'request': request,
                                          'page_title': 'Мониторинг',
                                      }
                                      )
