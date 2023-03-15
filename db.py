from sqlalchemy import create_engine
from sqlalchemy import text
import config


class Database:
    engine = create_engine(config.ZABBIX_DATABASE_URI)

    def __init__(self):
        self.connection = self.engine.connect()
        print("DB Instance created")

    def fetch_by_query(self, query):
        fetch_query = self.connection.execute(text(f'select * from {query}'))

        for data in fetch_query.fetchall():
            print(data)
        return query
