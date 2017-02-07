from bs4 import BeautifulSoup, Tag
import requests
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from models import NbaGame, create_tables, db_connect


class YahooGameLog:
    def __init__(self, player_id):
        page = requests.get('http://sports.yahoo.com/nba/players/' + player_id + '/gamelog/')
        self.table = BeautifulSoup(page.text, 'lxml').find("table", attrs={"summary": "Player "})
        self.column_names = self.parse_headers()
        self.game_rows = self.parse_games()

    def parse_headers(self):
        names = []
        headers = self.table.find('thead').find_all('tr')[1]

        for header in headers:
            if isinstance(header, Tag):
                names.append(header.text)
        return names

    def parse_games(self):
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
        return games

    def update_games(self, session):
        print self.game_rows


def main():
    engine = db_connect()
    create_tables(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        game_log = YahooGameLog('4750')
        game_log.update_games(session)
    except:
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    main()




game_log = YahooGameLog('4750')