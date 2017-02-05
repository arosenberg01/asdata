from bs4 import BeautifulSoup, Tag
import requests

class YahooGameLog:
    def __init__(self, player_id):
        page = requests.get('http://sports.yahoo.com/nba/players/' + player_id + '/gamelog/')
        self.soup = BeautifulSoup(page.text, 'lxml')


