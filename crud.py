from sqlalchemy.orm import Session

from models import Host as ModelHost
from schema import Host as SchemaHost


def get_monitored_hosts(db: Session):
    return db.query(ModelHost).all()


def get_host(db: Session, hostid: int):
    return db.query(ModelHost).filter(ModelHost.hostid == hostid).first()


def add_host(db: Session, host: SchemaHost):
    db_host = ModelHost(hostid=host.hostid, column=host.column)
    db.add(db_host)
    db.commit()
    db.refresh(db_host)
    return db_host
