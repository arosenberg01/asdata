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

class NbaPlayer:
    def __init__(self, player_id):
        page = requests.get('http://sports.yahoo.com/nba/players/' + player_id + '/gamelog/')
        self.player_id = player_id
        self.soup = BeautifulSoup(page.text, 'lxml')
        self.info_section = self.soup.find('div', attrs={'id': 'mediasportsplayerheader'})
        self.table = self.soup.find('table', attrs={'summary': 'Player '})
        self.player_info = self.parse_info_section()
        self.game_log_columns = self.parse_game_log_columns()
        self.game_log = self.parse_game_log()

    def parse_game_log_columns(self):
        names = []
        headers = self.table.find('thead').find_all('tr')[1]

        for header in headers:
            if isinstance(header, Tag):
                names.append(header.text)
        return names

    def parse_game_log(self):
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

    def parse_info_section(self):
        top = self.info_section.find('div', attrs={'class': 'player-info'})
        team_info = top.find('span', attrs={'class': 'team-info'})
        num_and_pos = team_info.find(text=True).split(',')
        team = team_info
        height = self.info_section.find('li', attrs={'class': 'height'}).find('dd').find(text=True).split('-')
        inches = int(height[0]) * 12 + int(height[1])
        date = self.info_section.find('li', attrs={'class': 'born'}).find('dd').find(text=True).replace(',', '').split(' ')
        day = date[1] if len(date[1]) == 1 else '0' + date[1]
        born = datetime.strptime(date[2] + date[0] + day, '%Y%B%d')

        player_info = {
            'name': top.find('h1').find(text=True),
            'team': team_info.find('a').find(text=True),
            'number': num_and_pos[0].split('#')[1].encode('utf-8'),
            'pos': num_and_pos[1].encode('utf-8'),
            'height': inches,
            'weight': int(self.info_section.find('li', attrs={'class': 'weight'}).find('dd').find(text=True)),
            'born': born,

        }

        return player_info

    def update_player_info(self, session, force_update):
        # nba_player = NbaPlayer(
        #     id=self.player_id,
        #     name=name,
        #     team=team,
        #     pos=pos,
        #     height=height,
        #     weight=weight,
        #     born=born,
        # )

        # if session.query(NbaGame).filter(NbaGame.date == nba_game['date']).first() is None:
        if force_update or session.query(NbaPlayer). \
                filter(NbaPlayer.id == nba_player.id). \
                first() is None:

            session.add(nba_player)
        else:
            print('\n----------\nnba game already exists\n----------\n')

        return ''

    def update_games(self, session, force_update):

        for row in self.yahoo_rows:
            game_opp = row[1].split('@')
            is_away = True if len(game_opp) > 1 else False
            date = parse_date(row[0])
            seconds_played = sec_played(row[3])

            nba_game = NbaGame(
                yahoo_id=self.player_id,
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
                pts=row[21]
            )

            # if session.query(NbaGame).filter(NbaGame.date == nba_game['date']).first() is None:
            if force_update or session.query(NbaGame).\
                    filter(NbaGame.date == nba_game.date).\
                    filter(NbaGame.yahoo_id == nba_game.yahoo_id).\
                    first() is None:

                session.add(nba_game)
            else:
                print('\n----------\nnba game already exists\n----------\n')

class YahooNbaPlayer:
    def __init__(self, player_id):
        page = requests.get('http://sports.yahoo.com/nba/players/' + player_id + '/gamelog/')
        self.player_id = player_id
        self.table = BeautifulSoup(page.text, 'lxml').find("table", attrs={"summary": "Player "})
        self.column_names = self.parse_game_log_headers()
        self.yahoo_rows = self.parse_game_log()


def main(yahoo_ids):
    print('running')
    engine = db_connect()
    create_tables(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:


        session.commit()
    except Exception as e:
        print(e)
        session.rollback()
        raise
    finally:
        session.close()

# def update_games(session, yahoo_ids):
    # for yahoo_id in yahoo_ids:
        # game_log = YahooGameLog(yahoo_id)
        # game_log.update_games(session)

def update_players(session, yahoo_ids):
    for yahoo_id in yahoo_ids:
        nba_player = YahooNbaPlayer(yahoo_id)
        nba_player.update_info(session)

def handler(event, context):
    print(event)
    main(event['yahoo_ids'])

if __name__ == "__main__":
    # main(['4942'])
    nba_player = NbaPlayer('4942')

