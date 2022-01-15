from sqlalchemy import Column, Integer, String, func, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Butterfly(Base):
    __tablename__ = 'butterflies'
    id = Column(Integer, primary_key=True)
    rating = Column(Integer, index=True, nullable=False)
    # image_url = Column(String)

class Match(Base):
    __tablename__ = 'matches'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    voter_ip = Column(String(255), nullable=False)
    player_id = Column(Integer, nullable=False)
    opponent_id = Column(Integer, nullable=False)
    player_initial_rating = Column(Integer, nullable=False)
    player_final_rating = Column(Integer, nullable=False)
    opponent_initial_rating = Column(Integer, nullable=False)
    opponent_final_rating = Column(Integer, nullable=False)
