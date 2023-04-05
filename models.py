from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Host(Base):
    __tablename__ = 'host'
    hostid = Column(Integer, unique=True, primary_key=True, index=True)
    column = Column(Integer)
    image = Column(String)
