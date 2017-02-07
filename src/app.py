from bs4 import BeautifulSoup, Tag
import requests
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from models import NbaGame, create_tables, db_connect



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

    def map_yahoo_row_to_db_row(self):

        for row in self.yahoo_rows:
            game_opp = row[1].split('@')
            away = True if len(game_opp) > 1 else False

            NbaGame(yahoo_id=self.yahoo_id,
                    date=row[0],
                    opp=game_opp.pop(),
                    away=true,
                    score=row[2],
                    minutes=row[3],
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

    def update_games(self, session):
        print self.game_rows

def main():
    engine = db_connect()
    create_tables(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        game_log = YahooGameLog('4750')
        # game_log.update_games(session)
        for game in game_log.game_rows:
            print(game)

        nba_game = NbaGame()
    except:
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    main()

game_log = YahooGameLog('4750')