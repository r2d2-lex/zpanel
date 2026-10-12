import os

import pytest
from dotenv import load_dotenv
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from main import app
from models import Base

load_dotenv(Path(__file__).resolve().parent / ".env.test")
ZPANEL_DATABASE_URI = os.environ.get("ZPANEL_DATABASE_URI")
TEST_DATABASE_URI = os.environ.get("TEST_DATABASE_URI")
if not TEST_DATABASE_URI:
    raise RuntimeError('Для тестов нужно задать переменную окружения TEST_DATABASE_URI')
from db import get_db
engine_test = create_async_engine(TEST_DATABASE_URI, poolclass=NullPool)
async_session_maker = sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)
Base.metadata.bind = engine_test

async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield async_session_maker
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="session", autouse=True)
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
