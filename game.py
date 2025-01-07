import os
from typing import List, Optional
from dotenv import load_dotenv
from game_api import MonadCardGameAPI
from player_model import Player, BotPlayer


load_dotenv()

MONAD_API_BASE_URL = os.getenv("MONAD_API_BASE_URL")
MONAD_API_TOKEN = os.getenv("MONAD_API_TOKEN")
BOT_PLAYER_NAME = os.getenv("BOT_PLAYER_NAME")


class Game:
    def __init__(self, api_data: dict, bot_name: str):
        self.bot_name = bot_name
        self.api_data: dict = api_data
        self.game_id: Optional[str] = None
        self.bot_player: Optional[BotPlayer] = None
        self.table_money: int = 0  
        self.table_card: int = 0
        self.cardsLeft: int = 24
        self.finished: bool = False
        self.players: List[Player] = []


    def start(self):
        game_data = self.api_data.start_game()
        self.game_id = game_data["gameId"]
        self._update_game_state(game_data["status"])

        print("Game started: ", self.game_id)

        for player in game_data["status"]["players"]:
            if player["name"] == self.bot_name:
                self.bot_player = BotPlayer.from_json(player)
            else:
                self.players.append(Player.from_json(player))


    def update(self, state: dict):
        self._update_game_state(state["status"])

        for player in state["status"]["players"]:
            if player["name"] != self.bot_name:
                player_instance = next(p for p in self.players if p.name == player["name"])
                player_instance.update_state(player["money"], player["cards"], self.table_card)
            else:
                self.bot_player.update_state(player["money"], player["cards"], self.table_card)


    def _update_game_state(self, status: dict):
        self.table_card = status.get("card", 0) # On the last turn, there is no "card" field in the JSON response, the field "finished" = True 
        self.table_money = status["money"]
        self.cardsLeft = status["cardsLeft"]
        self.finished = status["finished"]


    def turn(self, pause: bool = False):
        print("----------------Turn----------------")
        print(f"On the table card: {self.table_card}, money: {self.table_money}, Cards left: {self.cardsLeft}")
        print(f"{self.bot_player.name} (Money: {self.bot_player.money}, Cards: {self.bot_player.cards}, Score: {self.bot_player.score}, Delta: {self.bot_player.min_delta})")

        for player in self.players:
            print(f"{player.name} (Money: {player.money}, Cards: {player.cards}, Score: {player.score}), Delta: {player.min_delta})")

        if pause:
            _ = input("Press enter to continue") # Waiting for tests

        take_card = self.bot_player.decide(self.table_card, self.table_money, self.cardsLeft, self.players)

        game_state = self.api_data.action(self.game_id, {"takeCard": take_card})

        self.update(game_state)



    def play(self):
        print("Welcome to the game!")
        pause_answer = input("Do you want to pause, after each turn? (y/n) ").lower()
        pause = True if pause_answer == "y" else False

        self.start()
        while not self.finished:
            self.turn(pause=pause)

        print("Game finished")

        print(f"{self.bot_player.name}, Score: {self.bot_player.score})")
        for player in self.players:
            print(f"{player.name}, Score: {player.score})")
        
        players = self.players + [self.bot_player]
        print("Winner is: ", min(players, key=lambda x: x.score).name)



if __name__ == "__main__":
    api = MonadCardGameAPI(MONAD_API_BASE_URL, MONAD_API_TOKEN, True)
    game = Game(api, BOT_PLAYER_NAME)
    game.play()
