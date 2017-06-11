import unittest

from utilities import (
    game_date,
    sec_played,
    schedule_date
)

# class TestGameDate(unittest.TestCase):
#     def test_game_date

class TestSecPlayed(unittest.TestCase):

    def test_sec_played_str_to_int(self):
        seconds = sec_played('00:00')
        self.assertTrue(type(seconds) is int)

    def test_sec_played_total(self):
        seconds = sec_played('31:17')
        self.assertEqual(seconds, 1877)

if __name__ == '__main__':
    unittest.main()