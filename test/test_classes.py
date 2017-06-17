import unittest
from unittest.mock import Mock
import os
import gzip
import bs4
from classes import (
    NbaTeamPage,
    NbaPlayerPage
)

class TestNbaTeamPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        file_path = os.path.join(os.path.dirname(__file__), 'mock_data/nba_roster_lakers.htm.gz')
        cls.html = gzip.open(file_path).read()

    @classmethod
    def setUp(cls):
        cls.request_mock = Mock()
        cls.parse_mock = Mock()
        cls.session_mock = Mock()
        cls.nba_team = NbaTeamPage('okc', cls.request_mock, bs4)
        cls.soup = cls.nba_team.convert(cls.html)

    def test_get_should_call_requester_get(self):
        self.nba_team.get(self.nba_team.url)
        self.request_mock.get.assert_called_once()

    def test_parse_roster_should_return_player_ids(self):
        expected = ['5383', '4285', '5357', '3824', '5329', '5601', '4794', '5487', '5762',
            '5318', '5011', '5433', '3339', '4294', '5663']
        player_ids = self.nba_team.parse_roster(self.soup)
        self.assertEqual(expected, player_ids)

    def test_update_team_calls_session_methods(self):
        self.nba_team.update_team(self.session_mock, '', [])
        self.session_mock.query.assert_called_once()
        self.session_mock.add.assert_called_once()

class TestNbaPlayerPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        file_path = os.path.join(os.path.dirname(__file__), 'mock_data/nba_player_ingram.htm.gz')
        cls.html = gzip.open(file_path).read()

    @classmethod
    def setUp(cls):
        cls.request_mock = Mock()
        cls.parse_mock = Mock()
        cls.session_mock = Mock()
        cls.nba_player = NbaPlayerPage('5601', cls.request_mock, bs4)
        cls.soup = cls.nba_player.convert(cls.html)

    def test_get_should_call_requester_get(self):
        self.nba_player.get(self.nba_player.url)
        self.request_mock.get.assert_called_once()

    def test_games_returns_game_log(self):
        expected_columns = ['Date', 'Opp', 'Score', 'Type', 'Min', 'FGM', 'FGA', 'FG%', '3PM', '3PA', '3P%', 'FTM',
                            'FTA', 'FT%', 'OR', 'DR', 'Reb', 'Ast', 'TO', 'Stl', 'Blk', 'PF', 'Pts']
        expected_first_row = [None, '@GS', 'L 94-109', 'Reg', '29:26', '5', '16', '31.3', '0', '0', '-', '1', '2',
                              '50.0', '1', '4', '5', '5', '5', '3', '0', '2', '11']

        games = self.nba_player.parse_games(self.soup)
        self.assertListEqual(expected_columns, games['columns'])
        self.assertListEqual(expected_first_row, games['rows'][0])

if __name__ == '__main__':
    unittest.main()