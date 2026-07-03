import random
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class ClueGame:
    def __init__(self):
        """
        Initializes the Clue game with rooms, weapons, suspects, and generates the solution.
        """
        self.rooms = ["Kitchen", "Ballroom", "Conservatory", "Dining Room", "Billiard Room", "Library", "Lounge", "Hall", "Study"]
        self.weapons = ["Candlestick", "Dagger", "Lead Pipe", "Revolver", "Rope", "Wrench"]
        self.suspects = ["Miss Scarlet", "Colonel Mustard", "Mrs. White", "Mr. Green", "Mrs. Peacock", "Professor Plum"]
        self.solution = self.generate_solution()
        self.players = []
        self.clues = self.generate_clues()
        logging.info("Clue game initialized.")

    def generate_solution(self):
        """
        Randomly selects one room, one weapon, and one suspect to form the solution.
        """
        solution = {
            "room": random.choice(self.rooms),
            "weapon": random.choice(self.weapons),
            "suspect": random.choice(self.suspects)
        }
        logging.debug(f"Solution generated: {solution}")
        return solution

    def generate_clues(self):
        """
        Generates a shuffled list of all clues (rooms, weapons, suspects).
        """
        all_clues = self.rooms + self.weapons + self.suspects
        random.shuffle(all_clues)
        logging.debug(f"Clues generated: {all_clues}")
        return all_clues

    def add_player(self, player):
        """
        Adds a player to the game.
        """
        self.players.append(player)
        logging.info(f"Player {player.name} added to the game.")

    def distribute_clues(self):
        """
        Distributes clues among players.
        """
        num_players = len(self.players)
        for i, clue in enumerate(self.clues):
            self.players[i % num_players].receive_clue(clue)
        logging.info("Clues distributed among players.")

    def make_suggestion(self, player, room, weapon, suspect):
        """
        Checks if the suggestion matches the solution.
        """
        if room == self.solution["room"] and weapon == self.solution["weapon"] and suspect == self.solution["suspect"]:
            logging.info(f"Suggestion by {player.name} matches the solution.")
            return True
        logging.info(f"Suggestion by {player.name} does not match the solution.")
        return False

    def make_accusation(self, player, room, weapon, suspect):
        """
        Checks if the accusation matches the solution and announces the result.
        """
        if self.make_suggestion(player, room, weapon, suspect):
            logging.info(f"{player.name} has solved the mystery!")
            print(f"{player.name} has solved the mystery!")
            return True
        else:
            logging.warning(f"{player.name}'s accusation is incorrect.")
            print(f"{player.name}'s accusation is incorrect.")
            return False
        
class Player:
    def __init__(self, name):
        """
        Initializes a player with a name, empty hand, and no location.
        """
        self.name = name
        self.hand = []
        self.location = None
        logging.info(f"Player {self.name} initialized.")

    def move_to(self, room):
        """
        Moves the player to a specified room.
        """
        self.location = room
        logging.debug(f"{self.name} moved to {room}.")

    def receive_clue(self, clue):
        """
        Adds a clue to the player's hand.
        """
        self.hand.append(clue)
        logging.debug(f"{self.name} received clue: {clue}.")

    def show_hand(self):
        """
        Returns the player's hand.
        """
        return self.hand
    
def main():
    """
    Main game loop where players take turns to move, make suggestions, and make accusations.
    """
    game = ClueGame()
    player1 = Player("Player 1")
    player2 = Player("Player 2")
    game.add_player(player1)
    game.add_player(player2)
    game.distribute_clues()

    players = [player1, player2]
    current_player_index = 0

    while True:
        current_player = players[current_player_index]
        print(f"\n{current_player.name}'s turn.")
        print(f"Current location: {current_player.location}")
        print(f"Your hand: {current_player.show_hand()}")

        action = input("Choose an action (move/suggest/accuse/quit): ").strip().lower()
        if action == "move":
            room = input(f"Choose a room to move to {game.rooms}: ").strip()
            if room in game.rooms:
                current_player.move_to(room)
                print(f"{current_player.name} moved to {room}.")
            else:
                logging.warning("Invalid room selected.")
                print("Invalid room.")
        elif action == "suggest":
            room = current_player.location
            weapon = input(f"Choose a weapon {game.weapons}: ").strip()
            suspect = input(f"Choose a suspect {game.suspects}: ").strip()
            if game.make_suggestion(current_player, room, weapon, suspect):
                print("Suggestion matches the solution!")
            else:
                print("Suggestion does not match the solution.")
        elif action == "accuse":
            room = input(f"Choose a room {game.rooms}: ").strip()
            weapon = input(f"Choose a weapon {game.weapons}: ").strip()
            suspect = input(f"Choose a suspect {game.suspects}: ").strip()
            if game.make_accusation(current_player, room, weapon, suspect):
                break
        elif action == "quit":
            logging.info("Game ended by player.")
            print("Game ended.")
            break
        else:
            logging.warning("Invalid action selected.")
            print("Invalid action.")

        current_player_index = (current_player_index + 1) % len(players)

if __name__ == "__main__":
    main()