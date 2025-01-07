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

with open("json_for_test/game_step-03.json") as f:
    data3 = json.load(f)["status"]


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
        self.assertEqual(self.player.min_delta, 0)

        self.player.update_state(10, [[5, 6]], 4)
        self.player.calculate_deltas = 8
        self.assertEqual(self.player.min_delta, 2)

        self.player.update_state(10, [[5, 6]], 7)
        self.assertEqual(self.player.min_delta, 1)

        self.player.update_state(10, [[5, 6]], 4)
        self.assertEqual(self.player.min_delta, -1)

    def test_update_state(self):
        self.player.update_state(10, [[5]], 7)
        self.assertEqual(self.player.money, 10)
        self.assertEqual(self.player.cards, [[5]])
        self.assertEqual(self.player.min_delta, 2)
        
        self.player.update_state(5, [[5, 6], [12]], 9)
        self.assertEqual(self.player.money, 5)
        self.assertEqual(self.player.cards, [[5, 6], [12]])
        self.assertEqual(self.player.min_delta, 3)

        self.player.update_state(5, [[5, 6], [12]], 10)
        self.assertEqual(self.player.money, 5)
        self.assertEqual(self.player.cards, [[5, 6], [12]])
        self.assertEqual(self.player.min_delta, -2)


class TestBotPlayer(unittest.TestCase):
    def setUp(self):
        self.bot_player = BotPlayer.from_json(data2["players"][0])
        
        self.players = []
        for player in data2["players"]:
            if player["name"] != "SergeiVasilyev":
                self.players.append(Player.from_json(player))
    

    def _update_players_state(self, table_card: int):
        for player in self.players + [self.bot_player]:
            player.update_state(player.money, player.cards, table_card)


    def test_is_possible_to_collect_series(self):
        print("-------test_is_possible_to_collect_series-------")
        self._update_players_state(19)
        # If BotPlayer has cards [16, 17] and on the table card 19 (delta = 2) and someone has card 18 (delta = 1), then BotPlayer should bet
        self.assertEqual(self.bot_player.is_possible_to_collect_series(self.players), False)
        self._update_players_state(14)
        self.assertEqual(self.bot_player.is_possible_to_collect_series(self.players), True)


    def test_decide(self):
        print("-------test_decide-------")
        table_card = 24
        self._update_players_state(table_card)
        self.assertEqual(self.bot_player.decide(table_card, 4, 24, self.players), True) # Take if the first move and enough money
        self.assertEqual(self.bot_player.decide(table_card, 1, 24, self.players), False) # Not enough money on the table

        table_card = 8
        self._update_players_state(table_card)
        self.assertEqual(self.bot_player.decide(table_card, 2, 24, self.players), True) # If first card is less than 15 and table money is more than 1

        table_card = 5
        self._update_players_state(table_card)
        self.assertEqual(self.bot_player.decide(table_card, 0, 20, self.players), True) # One of the players has delta abs(1)
        table_card = 14
        self._update_players_state(table_card)
        self.assertEqual(self.bot_player.decide(table_card, 3, 20, self.players), True) # One of the players has no money and there is 3 coins on the table
        
        table_card = 8
        self._update_players_state(table_card)
        self.bot_player.money = 3
        self.assertEqual(self.bot_player.decide(table_card, 5, 20, self.players), True) # Take a card less than 10 if BotPlayer has less than 4 coins in pocket

        table_card = 14
        self._update_players_state(table_card)
        self.bot_player.money = 8
        self.assertEqual(self.bot_player.decide(table_card, 5, 20, self.players), True) # Take a card if the card is in the range 

        self.bot_player.cards = []
        table_card = 29
        self._update_players_state(table_card)
        self.assertEqual(self.bot_player.decide(table_card, 3, 20, self.players), False) # If no cards and table card is over 24

        self.bot_player.cards = [[10]]
        table_card = 27
        self._update_players_state(table_card)
        self.assertEqual(self.bot_player.decide(table_card, 12, 20, self.players), True)





if __name__ == "__main__":
    unittest.main()
