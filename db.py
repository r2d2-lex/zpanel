from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from models import Base
import config
import logging

engine = create_engine(config.ZABBIX_DATABASE_URI, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Database:
    def __init__(self):
        self.connection = None
        self.engine = create_engine(config.ZABBIX_DATABASE_URI)

    def __enter__(self):
        try:
            self.connection = self.engine.connect()
        except OperationalError:
            logging.error('database "zpanel" does not exist')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection is not None:
            self.connection.close()
            logging.info('Database connection closed!')

    def create_db(self):
        Base.metadata.create_all(bind=self.engine)
        return

    def fetch_by_query(self, query):
        fetch_query = self.connection.execute(text(f'select * from {query}'))

        for data in fetch_query.fetchall():
            print(data)
        return query


def create_tables():
    with Database() as db:
        db.create_db()


def main():
    create_tables()


if __name__ == '__main__':
    main()
