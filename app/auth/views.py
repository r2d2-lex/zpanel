import secrets
from typing import  Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import config

router = APIRouter(prefix='/auth', tags=['Auth'])

security = HTTPBasic()

def get_auth_user_username(
        credentials: Annotated[HTTPBasicCredentials, Depends(security) ]
) -> str:
    unauthed_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Неправильный логин или пароль',
        headers={'WWW-Authenticate':'Basic'},
    )
    if credentials.username not in config.ZPANEL_SETTINGS_LOGIN:
        raise unauthed_exception

    correct_password = config.ZPANEL_SETTINGS_PASSWORD
    if correct_password is None:
        raise unauthed_exception

    if not secrets.compare_digest(
            credentials.password.encode('utf-8'),
            correct_password.encode('utf-8'),
    ):
        raise unauthed_exception

    return credentials.username
