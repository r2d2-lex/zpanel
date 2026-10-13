import secrets
from typing import  Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from cipher import hash_password
from core.config import settings
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
    if credentials.username is settings.auth.login:
        raise unauthed_exception

    correct_password = settings.auth.hash_password
    if correct_password is None:
        raise unauthed_exception

    if not secrets.compare_digest(
            hash_password(credentials.password).encode('utf-8'),
            correct_password.encode('utf-8'),
    ):
        raise unauthed_exception

    return credentials.username
