import unittest

from utilities import (
    sec_played
)

class TestSecPlayed(unittest.TestCase):

    def test_sec_played_str_to_int(self):
        seconds = sec_played('00:00')
        self.assertTrue(type(seconds) is int)

    def test_sec_played_total(self):
        seconds = sec_played('31:17')
        self.assertEqual(seconds, 1877)

if __name__ == '__main__':
    unittest.main()