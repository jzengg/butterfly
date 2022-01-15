from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Butterfly(Base):
    __tablename__ = 'butterflies'
    id = Column(Integer, primary_key=True)
