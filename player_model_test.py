import json
import unittest
from player_model import Player

with open("json_for_test/game_start.json") as f:
    data = json.load(f)["status"]


class TestPlayer(unittest.TestCase):
    def setUp(self):
        self.player = Player.from_json(data["players"][0])
        self.player.is_bot = True

    def test_score(self):
        self.assertEqual(self.player.score, -11)

        self.player.update_state(10, [[5]], 7)
        self.assertEqual(self.player.score, -5)

        self.player.update_state(10, [[5, 6], [8]], 7)
        self.assertEqual(self.player.score, 3)

    def test_delta(self):
        self.assertEqual(self.player.calculate_delta, 0)

        self.player.update_state(10, [[5, 6]], 4)
        self.player.calculate_delta = 8
        self.assertEqual(self.player.calculate_delta, 2)

        self.player.update_state(10, [[5, 6]], 7)
        self.assertEqual(self.player.calculate_delta, 1)

        self.player.update_state(10, [[5, 6]], 4)
        self.assertEqual(self.player.calculate_delta, -1)

    def test_update_state(self):
        self.player.update_state(10, [[5]], 7)
        self.assertEqual(self.player.money, 10)
        self.assertEqual(self.player.cards, [[5]])
        self.assertEqual(self.player.calculate_delta, 2)
        
        self.player.update_state(5, [[5, 6], [12]], 9)
        self.assertEqual(self.player.money, 5)
        self.assertEqual(self.player.cards, [[5, 6], [12]])
        self.assertEqual(self.player.calculate_delta, 3)

        self.player.update_state(5, [[5, 6], [12]], 10)
        self.assertEqual(self.player.money, 5)
        self.assertEqual(self.player.cards, [[5, 6], [12]])
        self.assertEqual(self.player.calculate_delta, -2)

        

if __name__ == "__main__":
    unittest.main()
