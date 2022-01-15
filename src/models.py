from sqlalchemy import Column, Integer, String, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Butterfly(Base):
    __tablename__ = 'butterflies'
    id = Column(Integer, primary_key=True)
    # TODO add index to rating
    rating = Column(Integer, nullable=False, server_default=1600)
    # image_url = Column(String)

class Match(Base):
    __tablename__ = 'match'
    id = Column(Integer, primary_key=True)
    timestamp = Column(Timestamp, nullable=False, server_default=func.now())
    voter_ip = Column(String, nullable=False)
    player_id = Column(Integer, nullable=False)
    opponent_id = Column(Integer, nullable=False)
    player_initial_rating = Column(Integer, nullable=False)
    player_final_rating = Column(Integer, nullable=False)
    opponent_initial_rating = Column(Integer, nullable=False)
    opponent_final_rating = Column(Integer, nullable=False)
