from sqlalchemy import create_engine, Column, Integer, Float, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL
import settings

Base = declarative_base()

def db_connect():
    """
    Creates database connection using database settings from settings.py
    Returns sqlalchemy engine instance
    """
    print(URL(**settings.DATABASE))
    return create_engine(URL(**settings.DATABASE), echo=True)

def create_tables(engine):
    Base.metadata.create_all(engine)

class NbaGame(Base):
    """NBA player games table"""
    __tablename__ = 'nba_game'

    id = Column(Integer, primary_key=True)
    yahoo_id = Column(Integer)
    date = Column(String(15))
    opp = Column(String(15))
    away = Column(Boolean)
    score = Column(String(15))
    minutes = Column(String(15))
    fgm = Column(Integer)
    fga = Column(Integer)
    fg_pct = Column(Float)
    three_pm = Column(Integer)
    three_pa = Column(Integer)
    three_pct = Column(Float)
    ftm = Column(Integer)
    fta = Column(Integer)
    ft_pct = Column(Float)
    off_reb = Column(Integer)
    def_reb = Column(Integer)
    total_reb = Column(Integer)
    ast = Column(Integer)
    to = Column(Integer)
    stl = Column(Integer)
    blk = Column(Integer)
    pf = Column(Integer)
    pts = Column(Integer)

