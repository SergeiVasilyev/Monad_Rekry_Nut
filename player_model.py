from functools import reduce
from typing import List


class Player:
    """
    Base player class.
    """
    def __init__(self, name: str, money: int = 11, cards: List[int] = []):
        self.name = name
        self.money: int = money
        self.cards: List[int] = cards
        self._score: int = -11

        self._deltas: int = []
        self._min_delta: int = 0


    @classmethod
    def from_json(cls, json_data):
        return cls(**json_data)


    @property
    def score(self) -> int:
        if len(self.cards) != 0:
            self._score = reduce(lambda x, y: x + y, [card[0] for card in self.cards]) - self.money
        return self._score


    @property
    def min_delta(self) -> int:
        self._min_delta = min(self.calculate_deltas, key=abs) if len(self.calculate_deltas) != 0 else 0
        return self._min_delta


    @property
    def calculate_deltas(self) -> int:
        return self._deltas


    @calculate_deltas.setter
    def calculate_deltas(self, table_card: int) -> int:
        _deltas = []
        self._deltas = []
        if len(self.cards) != 0:
            for group_of_cards in self.cards:
                _delta = 0
                for card in [group_of_cards[0], group_of_cards[-1]]:
                    card_difference = table_card - card
                    if abs(card_difference) < abs(_delta) or _delta == 0:
                        _delta = card_difference
                _deltas.append(_delta)
            self._deltas = _deltas          


    def update_state(self, money: int, cards: List[int], table_card: int):
        self.money = money
        self.cards = cards
        self.calculate_deltas = table_card
        self.min_delta


class BotPlayer(Player):
    """
    Bot player class.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    
    def is_possible_to_collect_series(self, players: List[dict]) -> bool:
        if self.calculate_deltas:
            botPlayer_min_delta = self.min_delta
            for player in players:
                for delta in player.calculate_deltas:
                    if (delta > 0 and botPlayer_min_delta > 0 and delta < botPlayer_min_delta) or (delta < 0 and botPlayer_min_delta < 0 and delta > botPlayer_min_delta):
                        return False # not possible to collect series
        return True


    def decide(self, table_card: int, table_money: int, cards_left: int, players: List[dict]) -> bool:
        is_possible_to_collect_series = self.is_possible_to_collect_series(players)
        print(f"is_possible_to_collect_series: {is_possible_to_collect_series}")

        players_min_delatas = [player.min_delta for player in players]
        players_money = [player.money for player in players]

        # if it's the first move in the game
        if cards_left == 24 and table_card <= 24 and table_money > 3:
            print("If first table card is less or equal than 24 and table money is more than 1")
            return True
        
        # if it's the first move in the game and card is less or equal 15 and table money is more than 1
        if cards_left == 24 and table_card <= 15 and table_money > 1:
            print("If first card is less than 15 and table money is more than 1")
            return True

        # if the card is important for the BotPlayer and one of other player
        if abs(self.min_delta) == 1 and (1 in list(map(abs, players_min_delatas)) or 0 in players_money):
            print(self.min_delta, players_min_delatas)
            print("If card important for BotPlayer and one of other player, or one of opponent has no money")
            return True
        
        # Bet if there is no money on the table.
        if (table_money < 2 and self.money > 0 and table_card > 10 and self.min_delta != -1): #  and cards_left > 8
            print("Place a bet")
            return False
        
        # Take a card less than 10 if you have less than 4 coins in your pocket
        if cards_left < 24 and self.money < 4 and table_money > 4 and table_card < 10:
            print("Take a card less than 10 if you have less than 4 coins in your pocket")
            return True

        # Take a card if the card is in the range calculated by the formula (cards_left//8)+1
        if cards_left < 24 and 0 < abs(self.min_delta) <= (cards_left//8)+1 and is_possible_to_collect_series:
            print("Take a card if the card is in the range calculated by the formula (cards_left//8)+1", self.min_delta, " <= ", (cards_left//8)+1)
            return True
        
        # Take any card if there are no cards available yet and there is more than 5 money on the table.
        if cards_left < 24 and table_card <= 24 and table_money >= 5 and self.cards == []:
            print("Take any card if there are no cards available yet and there is more than 5 money on the table.")
            return True
        
        # Take a card if there is a lot of money on the table according to the coefficient snd self.money less than 10
        # Coefficient K = k_min + (k_max - k_min) * (table_card - x_min) / (x_max - x_min)
        # k_min = 0.3, k_max = 0.45, x_min = 3, x_max = 35
        if self.money < 10 and table_card < 28 and table_money / table_card > (0.3+(0.45-0.3)*(table_card-3)/(35-3)):
            print("Take a card if there is a lot of money on the table according to the coefficient snd self.money less than 10")
            return True
        
        # Take a card if there is no money in the pocket
        if self.money == 0:
            print("Take a card if there is no money in the pocket")
            return True

        print("In other cases place a bet - False")
        return False


