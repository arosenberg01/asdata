import unittest
from unittest.mock import Mock
import os
import gzip
import logging
import bs4
from classes import (
    NbaTeamPage
)

class MockRequests:
    def get(self, url):
        pass

class TestNbaTeamPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        file_path = os.path.join(os.path.dirname(__file__), 'mock_data/nba_roster_lakers.htm.gz')
        cls.roster_text = gzip.open(file_path).read()
        cls.requester = MockRequests()

    @classmethod
    def setUp(cls):
        cls.nba_team = NbaTeamPage('okc', cls.requester, bs4)
        cls.parsed = cls.nba_team.convert_page(cls.roster_text)
        cls.session_mock = Mock()

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

    def test_update_team_calls_session_methods(self):
        self.nba_team.update_team(self.session_mock, '', [])
        self.session_mock.query.assert_called_once()
        self.session_mock.add.assert_called_once()

# class TestNbaPlayerPage(unittest.TestCase):
#     @classmethod
#     def setUpClass(cls):
#         pass

#     @classmethod
#     def setUp(cls):
#         pass


if __name__ == '__main__':
    unittest.main()