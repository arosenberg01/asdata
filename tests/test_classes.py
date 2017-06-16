import unittest
import os
import gzip
import bs4
import logging
from classes import (
    NbaTeam
)

class MockRequests:
    def get(self, url):
        pass

class TestNbaTeamPage(unittest.TestCase):
    # read html file and ungzip

    @classmethod
    def setUpClass(cls):
        requester = MockRequests()
        # file_path = os.path.join(os.path.dirname(__file__), 'mock_data/nba_roster_lakers.htm.gz')
        # f = gzip.open(file_path)
        # content = f.read()

        cls.nba_team = NbaTeam('okc', requester, bs4)
        cls.roster_text = content


    def test_get_page(self):
        team_page = self.nba_team.get_page(self.nba_team.url)
        self.assertFalse(self.nba_team.failed)

if __name__ == '__main__':
    unittest.main()