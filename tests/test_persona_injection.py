import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from clue_ai_bridge import ClueAIBridge
from clue_game import Player, ClueGame


class PersonaInjectionTests(unittest.TestCase):
    def test_observation_includes_persona_details(self):
        game = ClueGame()
        player = Player("Mrs. White", "W", (0, 0))
        game.players = [player]

        observation = ClueAIBridge.construct_observation(game, player)

        self.assertEqual(observation["player_info"]["persona_name"], "Mrs. White")
        self.assertIn("housekeeper", observation["player_info"]["persona_description"].lower())


if __name__ == "__main__":
    unittest.main()
