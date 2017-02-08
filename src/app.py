from datetime import datetime
from bs4 import BeautifulSoup, Tag
import requests
from sqlalchemy import exists, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from models import NbaGame, create_tables, db_connect

def parse_date(date):
    beforeNYE = ['Oct', 'Nov', 'Dec']
    month_and_day = date.split(' ')
    month = month_and_day[0]
    day = month_and_day[1]
    year = '2016' if month in beforeNYE else '2017'

    if len(day) == 1:
        day = '0' + day

    return datetime.strptime(year + month + day, '%Y%b%d')

def sec_played(time):
    minutes_and_sec = time.split(':')

    return int(minutes_and_sec[0]) * 60 + int(minutes_and_sec[1])

class YahooGameLog:
    def __init__(self, player_id):
        page = requests.get('http://sports.yahoo.com/nba/players/' + player_id + '/gamelog/')
        self.player_id = player_id
        self.table = BeautifulSoup(page.text, 'lxml').find("table", attrs={"summary": "Player "})
        self.column_names = self.parse_headers()
        self.yahoo_rows = self.parse_yahoo_game_log()

    def parse_headers(self):
        names = []
        headers = self.table.find('thead').find_all('tr')[1]

        for header in headers:
            if isinstance(header, Tag):
                names.append(header.text)
        return names

    def parse_yahoo_game_log(self):
        games = []
        rows = self.table.find('tbody').find_all('tr')
        for row in rows:
            game = []
            header_col = row.find_all('th')[0]
            cols = row.find_all('td')

            game.append(header_col.find(text=True))

            for cell in cols:
                game.append(cell.find(text=True))

            games.append(game)
        games.pop()
        return games

    def update_games(self, session):

        for row in self.yahoo_rows:
            game_opp = row[1].split('@')
            is_away = True if len(game_opp) > 1 else False
            date = parse_date(row[0])
            seconds_played = sec_played(row[3])

            nba_game = NbaGame(yahoo_id=self.player_id,
                    date=date,
                    opp=game_opp.pop(),
                    away=is_away,
                    score=row[2],
                    sec_played=seconds_played,
                    fgm=row[4],
                    fga=row[5],
                    fg_pct=row[6],
                    three_pm=row[7],
                    three_pa=row[8],
                    three_pct=row[9],
                    ftm=row[10],
                    fta=row[11],
                    ft_pct=row[12],
                    off_reb=row[13],
                    def_reb=row[14],
                    total_reb=row[15],
                    ast=row[16],
                    to=row[17],
                    stl=row[18],
                    blk=row[19],
                    pf=row[20],
                    pts=row[21])

            # if session.query(NbaGame).filter(NbaGame.date == nba_game['date']).first() is None:
            if session.query(NbaGame).\
                    filter(NbaGame.date == nba_game.date).\
                    filter(NbaGame.yahoo_id == nba_game.yahoo_id).\
                    first() is None:

                session.add(nba_game)
            else:
                print('\n----------\nnba game already exists\n----------\n')

def main(yahoo_ids):
    try:
        engine = db_connect()
        create_tables(engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        for yahoo_id in yahoo_ids:
            game_log = YahooGameLog(yahoo_id)
            game_log.update_games(session)

        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

def handler(event, context):
    main(event.yahoo_ids)

if __name__ == "__main__":
    main(['4942'])
