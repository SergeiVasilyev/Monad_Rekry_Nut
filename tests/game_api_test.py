# tests/test_game_api.py
import sys
from pathlib import Path
import unittest
from unittest.mock import Mock, patch
sys.path.append(str(Path(__file__).resolve().parent.parent))
from game_api import MonadCardGameAPI

class TestMonadCardGameAPI(unittest.TestCase):

    def setUp(self):
        self.base_url = "https://example.com/api"
        self.api_token = "test_token"
        self.api_connect = True
        self.api = MonadCardGameAPI(self.base_url, self.api_token, self.api_connect)

    def test_init(self):
        self.assertEqual(self.api.base_url, self.base_url)
        self.assertEqual(self.api.api_token, self.api_token)
        self.assertTrue(self.api.api_connect)

    @patch('requests.post')
    def test_start_game(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {"gameId": "test_game_id", "status": {}}
        mock_post.return_value = mock_response
        response = self.api.start_game()
        self.assertEqual(response, {"gameId": "test_game_id", "status": {}})
        mock_post.assert_called_once_with(f"{self.base_url}/game/", headers={"Authorization": f"Bearer {self.api_token}"})

    @patch('requests.post')
    def test_action(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {"status": {}}
        mock_post.return_value = mock_response
        game_id = "test_game_id"
        action = {"takeCard": True}
        response = self.api.action(game_id, action)
        self.assertEqual(response, {"status": {}})
        mock_post.assert_called_once_with(f"{self.base_url}/game/{game_id}/action", json=action, headers={"Authorization": f"Bearer {self.api_token}"})

if __name__ == "__main__":
    unittest.main()