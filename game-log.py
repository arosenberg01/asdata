from bs4 import BeautifulSoup, Tag
import requests

class YahooGameLog:
    def __init__(self, player_id):
        page = requests.get('http://sports.yahoo.com/nba/players/' + player_id + '/gamelog/')
        self.soup = BeautifulSoup(page.text, 'lxml')
        self.column_names = self.get_headers()

    def get_headers(self):
        names = []
        table = self.soup.find("table", attrs={"summary": "Player "})
        headers = table.find('thead').find_all('tr')[1]

        for header in headers:
            if isinstance(header, Tag):
                names.append(header.text)
        return names

    def columns(self):
        return self.column_names


game_log = YahooGameLog('4750')
print(game_log.columns())


