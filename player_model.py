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
        self._delta: int = 0


    @classmethod
    def from_json(cls, json_data):
        return cls(**json_data)


    @property
    def score(self) -> int:
        if len(self.cards) != 0:
            self._score = reduce(lambda x, y: x + y, [card[0] for card in self.cards]) - self.money
        return self._score


    @property
    def calculate_delta(self) -> int:
        return self._delta


    @calculate_delta.setter
    def calculate_delta(self, table_card: int) -> int:
        """
        Calculate the difference between the current card on the table and the card closest to it in the player's hand.
        The difference is calculated as the absolute difference between the two cards. If the player has multiple cards in their hand with the same difference to the table card, the difference of the first card in the first group of cards is used. If the player has no cards in their hand, the difference is set to 0.
        """
        self._delta = 0
        if len(self.cards) != 0:
            for group_of_cards in self.cards:
                for card in [group_of_cards[0], group_of_cards[-1]]:
                    card_difference = table_card - card
                    if abs(card_difference) < abs(self._delta) or self._delta == 0:
                        self._delta = card_difference


    def update_state(self, money: int, cards: List[int], table_card: int):
        self.money = money
        self.cards = cards
        self.calculate_delta = table_card


class BotPlayer(Player):
    """
    Bot player class.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    def compare_deltas(self, players_deltas: List[int]) -> bool:
        """The function compares players deltas and the bot delta.
        Returns False if one of the players' delta is closer to zero.
        """
        if self.calculate_delta == 0:
            return False
        
        for player_delta in players_deltas:
            if (self.calculate_delta > 0 and player_delta > 0 and self.calculate_delta > player_delta) or (self.calculate_delta < 0 and player_delta < 0 and self.calculate_delta < player_delta):
                return False
            
        return True


    def decide(self, table_card: int, table_money: int, cards_left: int, players_deltas: List[int], players_money: List[int]) -> bool:

        # Check if BotPlayer has cards [16, 17] and on the table card 19 (delta = 2) and someone has card 18 (delta = 1), then BotPlayer should bet
        check_if_bot_delta_less_then_other_players_delta = self.compare_deltas(players_deltas)

        # if it's the first move in the game
        if cards_left == 24 and table_card <= 24 and table_money > 3:
            print("If first table card is less than 24 and table money is more than 1")
            return True
        
        # if it's the first move in the game and card is less or equal 10
        if cards_left == 24 and table_card <= 15 and table_money > 1:
            print("If first card is less than 10")
            return True

        # if the card is important for the BotPlayer and one of other player
        if abs(self.calculate_delta) == 1 and (1 in list(map(abs, players_deltas)) or 0 in players_money):
            print("If card important for BotPlayer and one of other player, or someone has no money")
            return True
        
        # Bet if there is no money on the table.
        if (table_money < 2 and self.money > 0 and table_card > 10 and self.calculate_delta != -1): #  and cards_left > 8
            print("Place a bet")
            return False
        
        # Take a card less than 10 if you have less than 4 coins in your pocket
        if cards_left < 24 and self.money < 4 and table_money > 4 and table_card < 10:
            print("Take a card less than 10 if you have less than 4 coins in your pocket")
            return True

        # Take a card if the card is in the range calculated by the formula (cards_left//8)+1
        if cards_left < 24 and abs(self.calculate_delta) <= (cards_left//8)+1 and check_if_bot_delta_less_then_other_players_delta:
            print("Take a card if the card is in the range calculated by the formula (cards_left//8)+1", self.calculate_delta, " <= ", (cards_left//8)+1)
            return True
        
        # Take any card if there are no cards available yet and there is more than 5 money on the table.
        if cards_left < 24 and table_money >= 5 and self.cards == []:
            print("Take any card if there are no cards available yet and there is more than 5 money on the table.")
            return True
        
        if table_card > 20 and table_money / table_card > (0.3+(0.46-0.3)*(table_card-3)/(35-3)):
            print("Take card if on the table a lot of money")
            return True
        
        # Take a card if there is no money in the pocket
        if self.money == 0:
            print("Take a card if there is no money in the pocket")
            return True

        print("In other cases place a bet - False")
        return False


