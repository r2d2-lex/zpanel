from sqlalchemy import create_engine
from sqlalchemy import text

from models import Host as ModelHost
from models import Base

import config
import logging


class Database:
    def __init__(self):
        self.connection = None
        self.engine = create_engine(config.ZABBIX_DATABASE_URI)

    def __enter__(self):
        self.connection = self.engine.connect()
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

    def get_hosts(self):
        hosts = self.connection.session.query(ModelHost).all()
        return hosts

    def add_host(self, host):
        host = ModelHost(hostid=host.hostid, column=host.column)
        self.connection.session.add(host)
        self.connection.session.commit()
        return host


def create_tables():
    with Database() as db:
        db.create_db()


def main():
    create_tables()


if __name__ == '__main__':
    main()
