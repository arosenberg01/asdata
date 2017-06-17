import logging
from datetime import datetime
from bs4 import BeautifulSoup, Tag, Comment
from models import NbaTeam, NbaGame, NbaPlayer
from utilities import game_date, sec_played, schedule_date, team_mappings

logger = logging.getLogger()

class NbaTeamPage:
    def __init__(self, team_id, requester, parser):
        self.failed = False
        self.url = 'http://sports.yahoo.com/nba/teams/%s/roster/' % team_id
        self.requester = requester
        self.parser = parser
        self.team_id = team_id
        self.player_ids = []
        self.page_text = None

    def get(self, url):
        self.page_text = self.requester.get(url)
        return self.page_text

    def convert(self, text):
        self.soup = self.parser.BeautifulSoup(text, 'lxml')
        return self.soup

    def parse_roster(self, soup):
        player_ids = []
        roster_rows = soup.find('div', attrs={'class': 'ys-roster-table'}).find('tbody').find_all('tr')

        for row in roster_rows:
            player_id = row.find_all('td')[1].find('a').get('href').split('/')[5]
            player_ids.append(player_id)

        self.player_ids = player_ids
        return player_ids


    def update_roster(self, session, player_ids):
        for player_id in player_ids:
            nba_player = NbaPlayerPage(player_id)
            nba_player.update_player_info(session)

    def update_team(self, session, team_id, player_ids):
        nba_team = session.query(NbaTeam).filter(NbaTeam.id == team_id).first()

        if nba_team is None:
            logger.info('\n----------\ncreating new team: true (%s)', self.team_id)
            nba_team = NbaTeam(id=team_id)
        else:
            logger.info('\n----------\ncreating new team: false (%s)', self.team_id)
            nba_team.players = player_ids

        session.add(nba_team)


class NbaPlayerPage:
    def __init__(self, player_id, requester, parser):
        self.url = 'http://sports.yahoo.com/nba/players/%s/gamelog/' % player_id
        self.player_id = player_id
        self.requester = requester
        self.parser = parser
        self.page_text = None

    def get(self, url):
        self.html = self.requester.get(url)
        return self.page_text

    def convert(self, html):
        self.soup = self.parser.BeautifulSoup(html.text, 'lxml')
        return self.soup

    def games(self, soup):
        games = []
        column_names = []
        table = soup.find('table', attrs={'class': 'graph-table'})

        if table is not None:
            rows = table.find('tbody').find_all('tr')
            column_headers = table.find('thead').find_all('tr')[1]

            for row in rows:
                game = []
                cells = row.find_all('td')

                if len(cells) > 1:
                    for cell in cells:
                        game.append(cell.find(text=True))

                games.append(game)
            games.pop()

            for header in column_headers:
                if isinstance(header, Tag):
                    column_names.append(header.text)

        self.games = {
            'columns': column_names,
            'rows': games
        }

        return self.games

    def parse_info_section(self, soup, player_id):
        new_info_section = soup.find('div', attrs={'class': 'ys-player'})
        new_name = new_info_section.find('span', attrs={'class': 'ys-name'}).find(text=True)
        row = new_info_section.find('div', attrs={'class': 'Row'}).find('span')
        num_pos_team = []

        for idx, val in enumerate(row):
            num_pos_team.append(val.find(text=True))

        new_number = num_pos_team[0].split('#')[1].encode('utf-8')
        new_pos = num_pos_team[1].encode('utf-8')
        new_team = team_mappings['city_full_to_abrv'][num_pos_team[2]]
        player_stats = new_info_section.find('div', attrs={'class': 'Fz(13px)'})
        height = 0
        weight = 0

        for section in player_stats:
            key = section.find('span').find(text=True)
            if key == 'Height':
                formatted_height = section.find_all('span')[2].find(text=True)
                split_height = formatted_height.split('\'')
                height = int(split_height[0]) * 12 + int(split_height[1].rstrip('"'))
            if key == 'Weight':
                weight = int(section.find_all('span')[2].find(text=True))

        player_info = {
            'id': player_id,
            'name': new_name,
            'team': new_team,
            'number': new_number,
            'pos': new_pos,
            'height': height,
            'weight': weight,
            'born': datetime(1970, 1, 1, 0, 0)
        }

        return player_info

    def update_player_info(self, player_id, player_info, session, force_update=False):
        nba_player = session.query(NbaPlayer).filter(NbaPlayer.id == player_id).first()

        if nba_player is None:
            # player doesn't exist
            logger.info('\n----------\ninserting nba player: %s', player_info['name'])
            nba_player = NbaPlayer(player_info)
        else:
            # player exists - update row
            logger.info('\n----------\nupdating nba player: %s', player_info['name'])

            for key, value in player_info.iteritems():
                setattr(nba_player, key, value)

        session.add(nba_player)

    def update_games(self, player_id, player_info, games, session, force_update=False):
        self.update_player_info(session, force_update)

        for idx, row in enumerate(games['rows']):
            print('IDX: %s', idx)

            if len(row) > 1:
                game_opp = row[1].split('@')
                is_away = True if len(game_opp) > 1 else False

                if row[0] is None:
                    date = datetime(2016, 10, 25, 0, 0)
                else:
                    date = game_date(row[0])

                seconds_played = sec_played(row[3])

                for i, value in enumerate(row):
                    if value == '-':
                        row[i] = '0'

                nba_game = NbaGame(
                    player_id=player_id,
                    game_num=idx,
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

                print('checking row')
                print(nba_game.game_num)

                # if session.query(NbaGame).filter(NbaGame.date == nba_game['date']).first() is None:
                if session.query(NbaGame).\
                    filter(NbaGame.game_num == nba_game.game_num).\
                    filter(NbaGame.player_id == nba_game.player_id).\
                    first() is None:

                    logger.info('\n----------\ninserting nba game (%s): true', player_info['name'])
                    session.add(nba_game)
                else:
                    logger.info('\n----------\ninserting nba game (%s): false', player_info['name'])



