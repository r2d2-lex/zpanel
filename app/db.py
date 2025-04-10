import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import config
import logging
logger = logging.getLogger(__name__)


engine = create_async_engine(config.ZPANEL_DATABASE_URI, pool_size=70, max_overflow=0)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def async_main() -> None:
    async with engine.begin() as conn:
        logger.info('Database create tables!')
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


def main():
    asyncio.run(async_main())


if __name__ == '__main__':
    main()
