import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import config
import logging

logging.basicConfig(level=config.LOGGING_LEVEL)

from common import BASE_DIR
from items.views import router as items_router
from hosts.views import router as hosts_router
from monitoring.views import router as monitoring_router
from settings.views import router as settings_router
from images.views import router as images_router

app = FastAPI()
app.include_router(items_router)
app.include_router(hosts_router)
app.include_router(monitoring_router)
app.include_router(settings_router)
app.include_router(images_router)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, 'static')), name="static")

if config.ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
