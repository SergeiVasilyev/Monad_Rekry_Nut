import sys
from pathlib import Path
import json
import unittest
# Add the root directory of the project to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from player_model import Player, BotPlayer


with open("json_for_test/game_start.json") as f:
    data = json.load(f)["status"]

with open("json_for_test/game_step-02.json") as f:
    data2 = json.load(f)["status"]


class TestPlayer(unittest.TestCase):
    def setUp(self):
        self.player = Player.from_json(data["players"][0])

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


class TestBotPlayer(unittest.TestCase):
    def setUp(self):
        self.bot_player = BotPlayer.from_json(data2["players"][0])
        
        self.players = []
        for player in data2["players"]:
            if player["name"] != "SergeiVasilyev":
                self.players.append(Player.from_json(player))


    def test_compare_deltas(self):
        self.bot_player.calculate_delta = 19
        # If BotPlayer has cards [16, 17] and on the table card 19 (delta = 2) and someone has card 18 (delta = 1), then BotPlayer should bet
        self.assertEqual(self.bot_player.compare_deltas([3, 5, 3]), True)
        self.assertEqual(self.bot_player.compare_deltas([1, 5, 3]), False)


    def test_decide(self):
        self.bot_player.calculate_delta = card = 24
        self.assertEqual(self.bot_player.decide(card, 4, 24, [0, 0, 0], [11, 11, 11]), True)
        self.assertEqual(self.bot_player.decide(card, 1, 24, [0, 0, 0], [11, 11, 11]), False)

        self.bot_player.calculate_delta = card = 8
        self.assertEqual(self.bot_player.decide(card, 2, 24, [2, 5, 3], [11, 11, 11]), True)

        self.bot_player.calculate_delta = card = 14
        self.assertEqual(self.bot_player.decide(card, 0, 20, [2, -1, 3], [9, 9, 9]), True) # One of the players has delta abs(1)
        self.assertEqual(self.bot_player.decide(card, 0, 20, [2, 5, 3], [9, 0, 9]), True) # One of the players has no money
        
        self.bot_player.calculate_delta = card = 8
        self.bot_player.money = 3
        self.assertEqual(self.bot_player.decide(card, 5, 20, [2, 5, 3], [9, 9, 9]), True) # If BotPlayer has less than 4 coins in his pocket

        self.bot_player.calculate_delta = card = 14
        self.bot_player.money = 8
        self.assertEqual(self.bot_player.decide(card, 5, 20, [2, 5, 3], [9, 9, 9]), True) # Take a card if the card is in the range calculated by the formula (cards_left//8)+1

        self.bot_player.cards = []
        self.bot_player.calculate_delta = card = 30
        self.assertEqual(self.bot_player.decide(card, 3, 20, [4, 5, 3], [9, 9, 9]), False)

        self.bot_player.cards = [[10]]
        self.bot_player.calculate_delta = card = 28
        self.assertEqual(self.bot_player.decide(card, 13, 20, [4, 5, 3], [9, 9, 9]), True)







if __name__ == "__main__":
    unittest.main()
