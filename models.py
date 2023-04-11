from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Host(Base):
    __tablename__ = 'host'
    hostid = Column(Integer, unique=True, primary_key=True, index=True)
    column = Column(Integer)
    image = Column(String)


class MonitoredItem(Base):
    __tablename__ = 'item'
    host_id = Column(Integer, ForeignKey(Host.hostid), nullable=False, primary_key=True)
    name = Column(String)
    value_type = Column(String)
