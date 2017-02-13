import requests
import logging
from bs4 import BeautifulSoup
from src.db.models.model import NbaTeam

logger = logging.getLogger()

class NbaTeamPage:
    def __init__(self, team_id):
        page = requests.get('http://sports.yahoo.com/nba/teams/' + team_id + '/roster/')
        self.team_id = team_id
        self.soup = BeautifulSoup(page.text, 'lxml')
        self.roster = self.parse_roster()

    def parse_roster(self):
        player_ids = []
        roster_rows = self.soup.find('div', attrs={'class': 'ys-roster-table'}).find('tbody').find_all('tr')

        for row in roster_rows:
            player_id = cells = row.find_all('td')[1].find('a').get('href').split('/')[3]
            player_ids.append(player_id)

        return player_ids


    def update_roster(self, player_ids, session):
        nba_team = NbaTeam.query.filter_by(id=self.team_id).first()

        if nba_team is None:
            nba_team = NbaTeam(
                id=self.team_id,
                players=player_ids
            )
        else:
            nba_team.players = player_ids

        session.add(nba_team)
