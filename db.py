from sqlalchemy import create_engine
from sqlalchemy import text
import config
import logging


class Database:
    engine = create_engine(config.ZABBIX_DATABASE_URI)

    def __init__(self):
        self.connection = None

    def __enter__(self):
        self.connection = self.engine.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection is not None:
            self.connection.close()
            logging.info('Database connection closed!')

    def fetch_by_query(self, query):
        fetch_query = self.connection.execute(text(f'select * from {query}'))

        for data in fetch_query.fetchall():
            print(data)
        return query
