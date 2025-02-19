from typing import  Annotated
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

router = APIRouter(prefix='/auth', tags=['Auth'])

security = HTTPBasic()

@router.get('/login')
def basic_auth(
        credentials: Annotated[HTTPBasicCredentials, Depends(security) ]
):
    return {
        'username': credentials.username,
        'password': credentials.password,
    }
