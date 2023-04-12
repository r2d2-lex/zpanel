from sqlalchemy.orm import Session

from models import Host as ModelHost
from models import MonitoredItem as ModelMonitoredItem
from schema import Item as SchemaItem
from schema import Host as SchemaHost
from schema import HostImage as SchemaImageHost


# --------------------- ОПЕРАЦИИ С MonitoredItem -------------------- #

def get_items(db: Session, host_id: int):
    return db.query(ModelMonitoredItem).filter(ModelMonitoredItem.host_id == host_id).all()


def get_item(db: Session, item: SchemaItem):
    return db.query(ModelMonitoredItem).filter(ModelMonitoredItem.host_id == item.host_id,
                                               ModelMonitoredItem.name == item.name).first()


def add_item(db: Session, item: SchemaItem):
    db_item = ModelMonitoredItem(host_id=item.host_id, name=item.name, value_type=item.value_type)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def delete_item(db: Session, host_id: int, name: str):
    db_item = db.query(ModelMonitoredItem).filter(ModelMonitoredItem.host_id == host_id,
                                                  ModelMonitoredItem.name == name,
                                                  ).first()
    if db_item:
        db.delete(db_item)
        db.commit()
    return db_item


def update_item(db: Session, item: SchemaItem):
    db_item = db.query(ModelMonitoredItem).filter(ModelMonitoredItem.host_id == item.host_id).first()
    if db_item:
        db.query(ModelMonitoredItem).filter(ModelMonitoredItem.host_id == item.host_id,
                                            ModelMonitoredItem.name == item.name,
                                            ).update(item.dict())
        db.commit()
        db.refresh(db_item)
    return db_item


# --------------------- ОПЕРАЦИИ С Host -------------------- #

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


def update_host_image(db: Session, host: SchemaImageHost, image_name: str):
    db_host = db.query(ModelHost).filter(ModelHost.hostid == host.hostid).first()
    if db_host:
        db.query(ModelHost).filter(ModelHost.hostid == host.hostid).update({'image': image_name})
        db.commit()
        db.refresh(db_host)
    return db_host
