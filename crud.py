from sqlalchemy.orm import Session

from models import Host as ModelHost
from schema import Host as SchemaHost


def get_hosts(db: Session):
    return db.query(ModelHost).all()


def add_host(db: Session, host: SchemaHost):
    db_host = ModelHost(hostid=host.hostid, column=host.column)
    db.add(db_host)
    db.commit()
    db.refresh(db_host)
    return db_host
