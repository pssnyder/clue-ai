import random
import os
import sys
import time

# Attempt to import the AI bridge dynamically
try:
    from clue_ai_bridge import ClueAIBridge
except ImportError:
    ClueAIBridge = None

class ClueGame:
    def __init__(self):
        # 11x11 Grid Coordinate Definitions for Rooms
        # Rooms contain wall coordinates, a designated entry door coordinate, and a single letter identifier
        self.rooms = {
            "Study": {
                "coords": [(r, c) for r in range(3) for c in range(3)], 
                "door": (2, 1), "char": "S"
            },
            "Hall": {
                "coords": [(r, c) for r in range(3) for c in range(4, 7)], 
                "door": (2, 5), "char": "H"
            },
            "Lounge": {
                "coords": [(r, c) for r in range(3) for c in range(8, 11)], 
                "door": (2, 9), "char": "O"
            },
            "Library": {
                "coords": [(r, c) for r in range(4, 7) for c in range(3)], 
                "door": (5, 2), "char": "L"
            },
            "Billiard Room": {
                "coords": [(r, c) for r in range(4, 7) for c in range(4, 7)], 
                "door": (4, 5), "char": "B"
            },
            "Dining Room": {
                "coords": [(r, c) for r in range(4, 7) for c in range(8, 11)], 
                "door": (5, 8), "char": "I"
            },
            "Conservatory": {
                "coords": [(r, c) for r in range(8, 11) for c in range(3)], 
                "door": (8, 1), "char": "C"
            },
            "Ballroom": {
                "coords": [(r, c) for r in range(8, 11) for c in range(4, 7)], 
                "door": (8, 5), "char": "A"
            },
            "Kitchen": {
                "coords": [(r, c) for r in range(8, 11) for c in range(8, 11)], 
                "door": (8, 9), "char": "K"
            }
        }
        
        self.room_names = list(self.rooms.keys())
        self.weapons = ["Candlestick", "Dagger", "Lead Pipe", "Revolver", "Rope", "Wrench"]
        self.suspects = ["Miss Scarlet", "Colonel Mustard", "Mrs. White", "Mr. Green", "Mrs. Peacock", "Professor Plum"]
        
        # Secret Solution Setup
        self.solution = {
            "room": random.choice(self.room_names),
            "weapon": random.choice(self.weapons),
            "suspect": random.choice(self.suspects)
        }
        
        self.players = []
        self.game_log = [
            "--- Clue Simulation Initialized ---",
            "Use keys to navigate or watch the AIs chat!",
            "----------------------------------"
        ]
        
        # Setup Card Deck
        self.all_clues = self.room_names + self.weapons + self.suspects
        solution_cards = list(self.solution.values())
        self.pool = [card for card in self.all_clues if card not in solution_cards]
        random.shuffle(self.pool)

    def add_log(self, sender, text, tag="SYSTEM"):
        """Appends events, chat records, or speech/thought bubbles directly to the display feed."""
        if tag == "SYSTEM":
            self.game_log.append(f"[SYS] {text}")
        elif tag == "EXTERNAL":
            self.game_log.append(f"[{sender}]: \"{text}\"")
        elif tag == "DISCOVERY":
            self.game_log.append(f"[★] {text}")

    def distribute_clues(self):
        """Evenly distributes the remaining Clue card pool among all registered players."""
        if not self.players:
            return
        for idx, card in enumerate(self.pool):
            self.players[idx % len(self.players)].hand.append(card)
        self.add_log("SYSTEM", "The mystery cards have been dealt secretly.")

    def get_room_at_coords(self, coords):
        """Returns the room name if the given coordinates are inside room boundaries."""
        for name, data in self.rooms.items():
            if coords in data["coords"]:
                return name
        return None

    def get_valid_moves(self, start_coords, roll=3):
        """Calculates valid coordinate targets on the grid using simple BFS navigation."""
        valid_targets = []
        queue = [(start_coords, 0)]
        visited = {start_coords}
        
        # Track where all players are positioned to block collisions on pathways
        player_positions = {p.coords for p in self.players if p.coords != start_coords}

        while queue:
            curr, dist = queue.pop(0)
            if dist > 0:
                valid_targets.append(curr)
            if dist == roll:
                continue

            cx, cy = curr
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = cx + dx, cy + dy
                neighbor = (nx, ny)
                
                # Check boundaries
                if 0 <= nx < 11 and 0 <= ny < 11:
                    if neighbor in visited or neighbor in player_positions:
                        continue
                    
                    # Verify if coordinate is a pathway space, a door, or wall space
                    room_at_neighbor = self.get_room_at_coords(neighbor)
                    
                    if room_at_neighbor is None:
                        # Standard Hallway
                        visited.add(neighbor)
                        queue.append((neighbor, dist + 1))
                    else:
                        # It is inside a room space. Can only enter through its door coordinate
                        door_coords = self.rooms[room_at_neighbor]["door"]
                        if curr == door_coords or neighbor == door_coords:
                            visited.add(neighbor)
                            queue.append((neighbor, dist + 1))
                            
        return list(set(valid_targets))

    def render_view(self):
        """Draws a split viewport rendering the ASCII board map and game events log."""
        os.system('cls' if os.name == 'nt' else 'clear')
        grid = [["." for _ in range(11)] for _ in range(11)]
        
        # Populate rooms and walls
        for r_name, r_data in self.rooms.items():
            first_coord = r_data["coords"][0]
            grid[first_coord[0]][first_coord[1]] = r_data["char"]
            for cx, cy in r_data["coords"]:
                if grid[cx][cy] == ".":
                    grid[cx][cy] = "x"
            # Draw Designated Doors
            dx, dy = r_data["door"]
            grid[dx][dy] = "d"

        # Overlay active Player tokens
        for p in self.players:
            px, py = p.coords
            grid[px][py] = p.token

        # Print layout header
        print("====================== CLUE SIMULATION BOARD ======================")
        print(" Map Representation                                 Game Event Log")
        print("-------------------------------------------------------------------")
        
        # Display the 11 lines of map alongside the latest log stream lines
        log_start = max(0, len(self.game_log) - 15)
        visible_logs = self.game_log[log_start:]
        
        for r in range(11):
            map_row = " ".join(grid[r])
            log_row = visible_logs[r] if r < len(visible_logs) else ""
            print(f"  {map_row}   │  {log_row}")
            
        print("-------------------------------------------------------------------")
        print(" Rooms: S=Study, H=Hall, O=Lounge, L=Library, B=Billiard, I=Dining")
        print("        C=Conservatory, A=Ballroom, K=Kitchen | d = Entry Doors")
        print("===================================================================")

class Player:
    def __init__(self, name, token, start_coords, is_human=False, ai_type=None):
        self.name = name
        self.token = token
        self.coords = start_coords
        self.hand = []
        self.is_human = is_human
        self.ai_type = ai_type

def bootstrap_agent_files():
    """Generates the necessary directories and files automatically to run out-of-the-box."""
    os.makedirs("clue_agent_v1", exist_ok=True)
    
    # Check and generate clue_agent_v1/agent.py
    agent_path = os.path.join("clue_agent_v1", "agent.py")
    if not os.path.exists(agent_path):
        agent_code = """import random

class ClueAgent:
    def __init__(self, name):
        self.name = name
        # Internal Virtual Notepad to keep track of eliminations
        self.notepad = {
            "rooms": {},
            "weapons": {},
            "suspects": {}
        }

    def initialize_notepad(self, observation):
        \"\"\"Initializes the notepad, marking off cards in hand as eliminated.\"\"\"
        valid = observation["valid_options"]
        my_hand = observation["player_info"]["hand"]
        
        for r in valid["rooms"]:
            self.notepad["rooms"][r] = "HELD" if r in my_hand else "UNKNOWN"
        for w in valid["weapons"]:
            self.notepad["weapons"][w] = "HELD" if w in my_hand else "UNKNOWN"
        for s in valid["suspects"]:
            self.notepad["suspects"][s] = "HELD" if s in my_hand else "UNKNOWN"

    def update_notepad_from_logs(self, history):
        \"\"\"Analyzes public game logs to logically cross out elements.\"\"\"
        pass

    def take_action(self, observation):
        \"\"\"Executes reasoning logic to move, suggest, or accuse.\"\"\"
        if not self.notepad["rooms"]:
            self.initialize_notepad(observation)
            
        self.update_notepad_from_logs(observation["public_history"])
        
        # Calculate options
        unknown_suspects = [s for s, status in self.notepad["suspects"].items() if status == "UNKNOWN"]
        unknown_weapons = [w for w, status in self.notepad["weapons"].items() if status == "UNKNOWN"]
        unknown_rooms = [r for r, status in self.notepad["rooms"].items() if status == "UNKNOWN"]
        
        # Game winning Accusation check
        if len(unknown_suspects) == 1 and len(unknown_weapons) == 1 and len(unknown_rooms) == 1:
            acc_suspect = unknown_suspects[0]
            acc_weapon = unknown_weapons[0]
            acc_room = unknown_rooms[0]
            return {
                "internal_thought": f"The deduction is mathematically complete! It must be {acc_suspect} in the {acc_room} with the {acc_weapon}.",
                "external_thought": "The puzzle is complete. I declare an accusation!",
                "action_type": "ACCUSE",
                "accusation": {"suspect": acc_suspect, "weapon": acc_weapon, "room": acc_room}
            }
            
        # Normal play cycle: Move towards an uneliminated room to make a suggestion
        current_room = observation["player_info"]["current_room"]
        
        if current_room and current_room in unknown_rooms:
            # We are already in an uneliminated room. Make a suggestion!
            sug_suspect = random.choice(unknown_suspects) if unknown_suspects else "Miss Scarlet"
            sug_weapon = random.choice(unknown_weapons) if unknown_weapons else "Dagger"
            
            return {
                "internal_thought": f"I am searching the {current_room}. Let's test the probability of {sug_suspect} using the {sug_weapon}.",
                "external_thought": f"I suggest it was {sug_suspect} in the {current_room} with the {sug_weapon}.",
                "action_type": "SUGGEST",
                "suggestion": {"suspect": sug_suspect, "weapon": sug_weapon, "room": current_room}
            }
        
        # Navigate to a new target
        valid_coordinates = observation["player_info"]["valid_coordinate_moves"]
        chosen_coord = random.choice(valid_coordinates) if valid_coordinates else observation["player_info"]["position"]
        
        # Determine internal commentary for immersion
        internal_monologue = f"Moving to tile {chosen_coord} searching for an accessible uneliminated room."
        banter_options = [
            "Gathering clues in the hallways...",
            "Searching for clues near the doorways.",
            "Analyzing spatial anomalies..."
        ]
        
        return {
            "internal_thought": internal_monologue,
            "external_thought": random.choice(banter_options),
            "action_type": "MOVE",
            "move_target": chosen_coord
        }
"""
        with open(agent_path, "w") as f:
            f.write(agent_code)
            
    # Touch clue_agent_v1/__init__.py
    init_path = os.path.join("clue_agent_v1", "__init__.py")
    if not os.path.exists(init_path):
        with open(init_path, "w") as f:
            f.write("")

def run_simulation():
    # Bootstrap game workspace
    bootstrap_agent_files()
    
    # Reload engine variables if the bridge was compiled during boot setup
    global ClueAIBridge
    if ClueAIBridge is None:
        try:
            from clue_ai_bridge import ClueAIBridge
        except ImportError:
            pass

    game = ClueGame()
    
    # Startup Configuration Menu
    os.system('cls' if os.name == 'nt' else 'clear')
    print("===================================================================")
    print("               CLUE SOCIAL SIMULATION CONSOLE SETUP               ")
    print("===================================================================")
    print("Choose Simulation Type:")
    print("  [1] Spectator Mode  -> Watch three AI Agents play collaboratively.")
    print("  [2] Active Play     -> Join as a human player alongside two AIs.")
    print("-------------------------------------------------------------------")
    
    mode_selection = input("Select Option [1-2, Default: 1]: ").strip() or "1"
    
    try:
        pace = float(input("\nConfigure Turn Pace (seconds of delay between turns) [Default: 2.0]: ").strip() or "2.0")
    except ValueError:
        pace = 2.0
        
    # Set up Player list based on selected mode
    if mode_selection == "2":
        # Interactive mode: Include Human Player P1
        p1 = Player("Pat (Human)", "P", (3, 3), is_human=True)
        p2 = Player("V7P3R_Bot", "V", (7, 3), is_human=False, ai_type="v1")
        p3 = Player("Snyder_Agent", "S", (3, 7), is_human=False, ai_type="v1")
        game.players = [p1, p2, p3]
        game.add_log("SYSTEM", "Active Player Mode setup loaded.")
    else:
        # Spectator Mode: Replace Human with an additional autonomous Agent
        p1 = Player("A_H_Bot", "A", (3, 3), is_human=False, ai_type="v1")
        p2 = Player("V7P3R_Bot", "V", (7, 3), is_human=False, ai_type="v1")
        p3 = Player("Snyder_Agent", "S", (3, 7), is_human=False, ai_type="v1")
        game.players = [p1, p2, p3]
        game.add_log("SYSTEM", "Spectator Mode setup successfully initialized.")

    game.distribute_clues()
    
    turn_counter = 0
    max_turns = 100
    
    while turn_counter < max_turns:
        for player in game.players:
            game.render_view()
            
            if player.is_human:
                # Human player input selection loop
                print(f"\n★ [YOUR TURN - {player.name}] ★")
                print(f"Cards in your Hand: {player.hand}")
                roll = random.randint(2, 4)
                print(f"You rolled a: {roll}")
                
                valid_moves = game.get_valid_moves(player.coords, roll)
                
                print("Options:")
                print(" [1] Move & Traverse Grid")
                print(" [2] Broadcast Chat Message to everyone")
                print(" [3] Make Suggestion (If currently inside a Room)")
                print(" [4] Make Accusation")
                print(" [5] Quit Simulation")
                
                choice = input("Select operation index: ").strip()
                
                if choice == "1":
                    print("\nSelect target coordinate index:")
                    for idx, m in enumerate(valid_moves):
                        room_label = game.get_room_at_coords(m)
                        label = f"Room: {room_label}" if room_label else "Hallway"
                        print(f"  [{idx}] Coordinate: {m} ({label})")
                    try:
                        move_idx = int(input("Enter index number: ").strip())
                        if 0 <= move_idx < len(valid_moves):
                            player.coords = valid_moves[move_idx]
                            room_label = game.get_room_at_coords(player.coords)
                            if room_label:
                                game.add_log(player.name, f"Entered Room: {room_label}", tag="SYSTEM")
                            else:
                                game.add_log(player.name, f"Moved on grid coordinates to {player.coords}", tag="SYSTEM")
                    except Exception:
                        print("Invalid selection. Passing turn...")
                        time.sleep(1)
                        
                elif choice == "2":
                    msg = input("Type public broadcast chat message: ")
                    game.add_log(player.name, msg, tag="EXTERNAL")
                    
                elif choice == "3":
                    current_room = game.get_room_at_coords(player.coords)
                    if not current_room:
                        print("You must be inside a room to make a suggestion!")
                        time.sleep(1.5)
                        continue
                    
                    print(f"Weapons list: {game.weapons}")
                    sug_w = input("Type Weapon Name: ").strip()
                    print(f"Suspects list: {game.suspects}")
                    sug_s = input("Type Suspect Name: ").strip()
                    
                    game.add_log("SYSTEM", f"{player.name} suggests {sug_s} in the {current_room} with the {sug_w}")
                    if (sug_s == game.solution["suspect"] and 
                        sug_w == game.solution["weapon"] and 
                        current_room == game.solution["room"]):
                        game.add_log("SYSTEM", "The suggestion matches the hidden file parameters!", tag="DISCOVERY")
                    else:
                        game.add_log("SYSTEM", "The suggestion did not solve the mystery.", tag="SYSTEM")
                    time.sleep(1.5)
                    
                elif choice == "4":
                    r_acc = input("Accuse Room: ").strip()
                    w_acc = input("Accuse Weapon: ").strip()
                    s_acc = input("Accuse Suspect: ").strip()
                    
                    if (r_acc == game.solution["room"] and 
                        w_acc == game.solution["weapon"] and 
                        s_acc == game.solution["suspect"]):
                        game.add_log("SYSTEM", f"SOLVED! {player.name} solved the mystery!", tag="DISCOVERY")
                        game.render_view()
                        print(f"CONGRATULATIONS! The solution was indeed {game.solution}")
                        sys.exit(0)
                    else:
                        game.add_log("SYSTEM", f"INCORRECT accusation by {player.name}!", tag="SYSTEM")
                        time.sleep(1.5)
                        
                elif choice == "5":
                    sys.exit(0)
            else:
                # Automate AI processing loops through the AI Bridge wrapper interface
                if ClueAIBridge is not None:
                    game_over = ClueAIBridge.execute_agent_turn(game, player)
                    if game_over:
                        game.render_view()
                        print("\nSimulation completed successfully!")
                        sys.exit(0)
                    # Introduce configured delay pace so the visual board and logs are readable
                    time.sleep(pace)
                else:
                    print("AI Bridge code missing! Please create clue_ai_bridge.py.")
                    time.sleep(2)
            
        turn_counter += 1

if __name__ == "__main__":
    run_simulation()

# Remember to save and back up your work! 💾