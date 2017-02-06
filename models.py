from sqlalchemy import Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class NbaGame(Base):
    __tablename__ = 'nba_game'

    id = Column(Integer, primary_key=True)
    date = Column(String)
    opp = Column(String)
    score = Column(String)
    minutes = Column(String)
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

