import os

from fastapi.templating import Jinja2Templates
from pathlib import Path
import logging
import sys

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, 'templates'))

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)

# logger = logging.getLogger("my_fastapi_app")
logger = logging.getLogger(__name__)