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


def delete_host(db: Session, hostid: int):
    db_host = db.query(ModelHost).filter(ModelHost.hostid == hostid).first()
    if db_host:
        db.delete(db_host)
        db.commit()
    return db_host


def update_host(db: Session, host: SchemaHost):
    db_host = db.query(ModelHost).filter(ModelHost.hostid == host.hostid).first()
    if db_host:
        db.query(ModelHost).filter(ModelHost.hostid == host.hostid).update(host.dict())
        db.commit()
        db.refresh(db_host)
    return db_host
