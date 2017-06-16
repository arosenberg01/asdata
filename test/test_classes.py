import unittest
import os
import gzip
import bs4
import logging
from classes import (
    NbaTeam
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

class MockRequests:
    def get(self, url):
        pass

class TestNbaTeamPage(unittest.TestCase):
    # read html file and ungzip

    @classmethod
    def setUpClass(cls):
        file_path = os.path.join(os.path.dirname(__file__), 'mock_data/nba_roster_lakers.htm.gz')
        cls.roster_text = gzip.open(file_path).read()
        cls.requester = MockRequests()

    @classmethod
    def setUp(cls):
        cls.nba_team = NbaTeam('okc', cls.requester, bs4)
        cls.parsed = cls.nba_team.convert_page(cls.roster_text)

    def test_get_page_should_not_fail(self):
        team_page = self.nba_team.get_page(self.nba_team.url)
        self.assertFalse(self.nba_team.failed)

    def test_convert_page_should_not_fail(self):
        parsed_page = self.nba_team.convert_page(self.roster_text)
        self.assertFalse(self.nba_team.failed)

    def test_parse_roster_should_return_player_ids(self):
        expected = ['5383', '4285', '5357', '3824', '5329', '5601', '4794', '5487', '5762',
            '5318', '5011', '5433', '3339', '4294', '5663']
        player_ids = self.nba_team.parse_roster(self.parsed)
        self.assertEqual(expected, player_ids)

if __name__ == '__main__':
    unittest.main()