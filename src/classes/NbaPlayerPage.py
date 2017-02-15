import requests
import logging
from datetime import datetime
from bs4 import BeautifulSoup, Tag
from src.db.models.model import NbaGame, NbaPlayer
from src.utilities import game_date, sec_played, team_mappings

logger = logging.getLogger()

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
        if table is not None:
            rows = table.find('tbody').find_all('tr')
            column_headers = table.find('thead').find_all('tr')[1]

            for row in rows:
                game = []
                cells = row.find_all('td')

                if len(cells) > 1:
                    header_col = row.find_all('th')[0]
                    game.append(header_col.find(text=True))
                    for cell in cells:
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
        city = team_info.find('a').find(text=True)

        player_info = {
            'id': self.player_id,
            'name': top.find('h1').find(text=True),
            'team': team_mappings['city_full_to_abrv'][city],
            'number': num_and_pos[0].split('#')[1].encode('utf-8'),
            'pos': num_and_pos[1].encode('utf-8'),
            'height': inches,
            'weight': int(info_section.find('li', attrs={'class': 'weight'}).find('dd').find(text=True)),
            'born': born
        }

        return player_info

    def update_player_info(self, session, force_update=False):
        nba_player = session.query(NbaPlayer).filter(NbaPlayer.id == self.player_id).first()

        if nba_player is None:
            # player doesn't exist
            logger.info('\n----------\ninserting nba player: %s', self.player_info['name'])
            nba_player = NbaPlayer(**self.player_info)
        else:
            # player exists - update row
            logger.info('\n----------\nupdating nba player: %s', self.player_info['name'])

            for key, value in self.player_info.iteritems():
                setattr(nba_player, key, value)

        session.add(nba_player)

    def update_games(self, session, force_update=False):

        for row in self.game_log['rows']:

            if len(row) > 1:
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
                if session.query(NbaGame).\
                    filter(NbaGame.date == nba_game.date).\
                    filter(NbaGame.player_id == nba_game.player_id).\
                    first() is None:

                    logger.info('\n----------\ninserting nba game (%s): true', self.player_info['name'])
                    session.add(nba_game)
                else:
                    logger.info('\n----------\ninserting nba game (%s): false', self.player_info['name'])

