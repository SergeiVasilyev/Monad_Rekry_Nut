import os
from functools import reduce
from typing import List, Optional
from dotenv import load_dotenv
from game_api import MonadCardGameAPI
from player_model import Player, BotPlayer


load_dotenv()

MONAD_API_BASE_URL = os.getenv("MONAD_API_BASE_URL")
MONAD_API_TOKEN = os.getenv("MONAD_API_TOKEN")
BOT_PLAYER_NAME = os.getenv("BOT_PLAYER_NAME")


class Game:
    def __init__(self, bot_name: str):
        self.bot_name = bot_name
        self.api_data: dict = MonadCardGameAPI(MONAD_API_BASE_URL, MONAD_API_TOKEN, True)
        self.game_id: Optional[str] = None
        self.bot_player: Optional[BotPlayer] = None
        self.table_money: int = 0  
        self.table_card: int = 0
        self.cardsLeft: int = 24
        self.finished: bool = False
        self.players: List[Player] = []


    def start(self):
        game_data = self.api_data.start_game()
        self.table_card = game_data["status"]["card"]
        self.table_money = game_data["status"]["money"]
        self.cardsLeft = game_data["status"]["cardsLeft"]
        self.finished = game_data["status"]["finished"]

        self.game_id = game_data["gameId"]
        bot_data = reduce(lambda x, _: x if x["name"] == self.bot_name else {}, game_data["status"]["players"])
        self.bot_player = BotPlayer.from_json(bot_data)

        print("Game started: ", self.game_id)

        for player in game_data["status"]["players"]:
            if player["name"] != self.bot_name:
                self.players.append(BotPlayer.from_json(player))


    def update(self, state: dict):
        self.table_card = state.get("card", 0) # On the last turn, there is no "card" field in the JSON response, the field "finished" = True 
        self.table_money = state["money"]
        self.cardsLeft = state["cardsLeft"]
        self.finished = state["finished"]


        for player in state["players"]:
            if player["name"] != self.bot_name:
                player_instance = next(p for p in self.players if p.name == player["name"])
                player_instance.update_state(player["money"], player["cards"], self.table_card)
            else:
                self.bot_player.update_state(player["money"], player["cards"], self.table_card)


    def turn(self, pause: bool = False):
        print("----------------Turn----------------")
        print(f"On the table card: {self.table_card}, money: {self.table_money}, Cards left: {self.cardsLeft}")
        print(f"{self.bot_player.name} (Money: {self.bot_player.money}, Cards: {self.bot_player.cards}, Score: {self.bot_player.score}, Delta: {self.bot_player.calculate_delta})")

        for player in self.players:
            print(f"{player.name} (Money: {player.money}, Cards: {player.cards}, Score: {player.score})")

        if pause:
            _ = input("Press enter to continue") # Waiting for tests
        
        players_delatas = [player.calculate_delta for player in self.players]
        players_monyes = [player.money for player in self.players]

        take_card = self.bot_player.decide(self.table_card, self.table_money, self.cardsLeft, players_delatas, players_monyes)

        game_state = self.api_data.action(self.game_id, {"takeCard": take_card})

        self.update(game_state["status"])



    def play(self):
        print("Welcome to the game!")
        pause_answer = input("Do you want to pause, after each turn? (y/n) ")
        if pause_answer == "y":
            pause = True
        else:
            pause = False

        self.start()
        while not self.finished:
            self.turn(pause=pause)

        print("Game finished")



if __name__ == "__main__":
    game = Game(BOT_PLAYER_NAME)
    game.play()
