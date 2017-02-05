from bs4 import BeautifulSoup, Tag
import requests

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
            cols = row.find_all('td')

            for cell in cols:
                game.append(cell.find(text=True))

            games.append(game)
        return games

    def columns(self):
        return self.column_names

    def games(self):
        return self.game_rows





game_log = YahooGameLog('4750')
print(game_log.columns())
print(game_log.games())


