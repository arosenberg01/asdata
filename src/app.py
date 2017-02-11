import logging
import sys
from datetime import datetime
from bs4 import BeautifulSoup, Tag
import requests
from sqlalchemy.orm import sessionmaker
from models import NbaGame, NbaPlayer, create_tables, db_connect

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
logger.addHandler(handler)

def game_date(date):
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

class NbaPlayerPage:
    def __init__(self, player_id):
        page = requests.get('http://sports.yahoo.com/nba/players/' + player_id + '/gamelog/')
        self.player_id = player_id
        self.soup = BeautifulSoup(page.text, 'lxml')
        self.player_info = self.parse_info_section()
        self.game_log = self.parse_game_log()

    def parse_game_log(self):
        games = []
        column_names = []
        table = self.soup.find('table', attrs={'summary': 'Player '})
        rows = table.find('tbody').find_all('tr')
        column_headers = table.find('thead').find_all('tr')[1]

        for row in rows:
            game = []
            header_col = row.find_all('th')[0]
            cols = row.find_all('td')
            game.append(header_col.find(text=True))

            for cell in cols:
                game.append(cell.find(text=True))

            games.append(game)
        games.pop()

        for header in column_headers:
            if isinstance(header, Tag):
                column_names.append(header.text)

        return {
            'columns': column_names,
            'rows': games
        }

    def parse_info_section(self):
        info_section = self.soup.find('div', attrs={'id': 'mediasportsplayerheader'})
        top = info_section.find('div', attrs={'class': 'player-info'})
        team_info = top.find('span', attrs={'class': 'team-info'})
        num_and_pos = team_info.find(text=True).split(',')
        height = info_section.find('li', attrs={'class': 'height'}).find('dd').find(text=True).split('-')
        inches = int(height[0]) * 12 + int(height[1])
        date = info_section.find('li', attrs={'class': 'born'}).find('dd').find(text=True).replace(',', '').split(' ')
        day = date[1] if len(date[1]) == 2 else '0' + date[1]
        born = datetime.strptime(date[2] + date[0] + day, '%Y%B%d')

        player_info = {
            'name': top.find('h1').find(text=True),
            'team': team_info.find('a').find(text=True),
            'number': num_and_pos[0].split('#')[1].encode('utf-8'),
            'pos': num_and_pos[1].encode('utf-8'),
            'height': inches,
            'weight': int(info_section.find('li', attrs={'class': 'weight'}).find('dd').find(text=True)),
            'born': born
        }

        return player_info

    def update_player_info(self, session, force_update=False):
        nba_player = NbaPlayer(
            id=self.player_id,
            name=self.player_info['name'],
            team=self.player_info['team'],
            pos=self.player_info['pos'],
            height=self.player_info['height'],
            weight=self.player_info['weight'],
            born=self.player_info['born']
        )

        # if session.query(NbaGame).filter(NbaGame.date == nba_game['date']).first() is None:
        if force_update or session.query(NbaPlayer). \
                filter(NbaPlayer.id == nba_player.id). \
                first() is None:

            logger.info('\n----------\ninserting nba player: true\n')
            session.add(nba_player)
        else:
            logger.info('\n----------\ninserting nba player: false\n')

        return ''

    def update_games(self, session, force_update=False):

        for row in self.game_log['rows']:
            game_opp = row[1].split('@')
            is_away = True if len(game_opp) > 1 else False
            date = game_date(row[0])
            seconds_played = sec_played(row[3])

            nba_game = NbaGame(
                player_id=self.player_id,
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
                    filter(NbaGame.player_id == nba_game.player_id).\
                    first() is None:

                logger.info('\n----------\ninserting nba game: true\n')
                session.add(nba_game)
            else:
                logger.info('\n----------\ninserting nba game: false\n')

def main(yahoo_ids):
    try:
        engine = db_connect()
        create_tables(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        logger.info("SUCCESS: Connection to RDS mysql instance succeeded")
    except:
        logger.error("ERROR: Unexpected error: Could not connect to mysql instance.")
        sys.exit()

    try:
        for yahoo_id in yahoo_ids:
            nba_player = NbaPlayerPage(yahoo_id)
            nba_player.update_player_info(session)
            nba_player.update_games(session)

        # isaiah = session.query(NbaPlayer).filter_by(name='Isaiah Thomas').one()

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
        nba_player = NbaPlayerPage(yahoo_id)
        nba_player.update_info(session)

def handler(event, context):
    print(event)
    main(event['yahoo_ids'])

if __name__ == "__main__":
    main(['4750', '4942'])
    # nba_player = NbaPlayer('4942')

