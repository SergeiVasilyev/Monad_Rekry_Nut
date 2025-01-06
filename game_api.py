import requests
import json
from typing import Dict, Any



class MonadCardGameAPI():
    """Class for interacting with the game API."""

    def __init__(self, base_url: str, api_token: str, api_connect: bool = True):
        self.base_url = base_url
        self.api_token = api_token
        self.api_connect = api_connect

    def start_game(self) -> Dict[str, Any]:
        """
        Initiates a new game session by sending a POST request to the game API.
        """
        if not self.api_connect:
            with open("json_for_test/game_start.json") as f:
                self.data = json.load(f)
            return self.data

        try:
            response = requests.post(f"{self.base_url}/game/", headers={"Authorization": f"Bearer {self.api_token}"})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error starting the game: {e}")
    

    def action(self, game_id: str, action: Dict[str, bool]) -> Dict[str, Any]:
        """
        Makes a game step by sending a POST request to the game API.

        Args:
            game_id (str): The ID of the game to make a step in.
            action (Dict[str, bool]): The action to take card or make bet.
        Returns:
            Dict[str, Any]: The response from the game API.
        """

        if not self.api_connect:
            with open("json_for_test/game_step-01.json") as f:
                self.data = json.load(f)
            return self.data

        try:
            response = requests.post(f"{self.base_url}/game/{game_id}/action", json=action, headers={"Authorization": f"Bearer {self.api_token}"})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error making the step: {e}")
        

if __name__ == "__main__":
    api = MonadCardGameAPI("https://api.monadcard.com", "your_api_token", False)
    game = api.start_game()
    print(game)