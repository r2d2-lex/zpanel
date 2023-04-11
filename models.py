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
    id = Column(Integer, unique=True, index=True, autoincrement=True, nullable=False)
    hostid = Column(Integer, ForeignKey(Host.hostid, ondelete="CASCADE", onupdate="CASCADE"), nullable=False,
                    primary_key=True)
    name = Column(String)
    value_type = Column(String)
