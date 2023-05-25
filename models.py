from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Host(Base):
    __tablename__ = 'host'
    host_id = Column(Integer, unique=True, primary_key=True, index=True)
    column = Column(Integer)
    image = Column(String)
    name = Column(String)


# autoincrement=True!!!
class MonitoredItem(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True, autoincrement=True)
    host_id = Column(Integer, ForeignKey(Host.host_id, ondelete='CASCADE'))
    name = Column(String)
    value_type = Column(String)
