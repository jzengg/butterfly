from sqlalchemy import Column, Integer, String, func, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Butterfly(Base):
    __tablename__ = "butterflies"
    id = Column(Integer, primary_key=True)
    rating = Column(Integer, index=True, nullable=False)
    name = Column(String(255), nullable=False, index=True)
    image_url = Column(String(1000), nullable=False)


class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, server_default=func.now())
    session_id = Column(String(255), nullable=False, index=True)
    voter_ip = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    region = Column(String(255), nullable=False)
    country = Column(String(255), nullable=False)
    winner_id = Column(Integer, nullable=False)
    loser_id = Column(Integer, nullable=False)
    winner_initial_rating = Column(Integer, nullable=False)
    winner_final_rating = Column(Integer, nullable=False)
    loser_initial_rating = Column(Integer, nullable=False)
    loser_final_rating = Column(Integer, nullable=False)
    position = Column(Integer, nullable=False)
    comment = Column(String(255), nullable=True)


class SessionFraud(Base):
    __tablename__ = "session_frauds"
    id = Column(Integer, primary_key=True)
    worker_id = Column(Integer, index=True, nullable=True)
    session_id = Column(String(255), nullable=False, index=True)
    frequent_voting_count = Column(Integer, nullable=False, default=0)
    same_side_voting_count = Column(Integer, nullable=False, default=0)
    timestamp = Column(DateTime, nullable=False, server_default=func.now())
