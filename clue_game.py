import random
import os
import sys
import time

try:
    from clue_ai_bridge import ClueAIBridge
except ImportError:
    ClueAIBridge = None

class ClueGame:
    def __init__(self):
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
        
        self.solution = {
            "room": random.choice(self.room_names),
            "weapon": random.choice(self.weapons),
            "suspect": random.choice(self.suspects)
        }
        
        self.players = []
        self.game_log = [
            "--- Clue Simulation Initialized ---",
            "Watch local LLMs cooperate, strategize, and chat!",
            "----------------------------------"
        ]
        
        self.all_clues = self.room_names + self.weapons + self.suspects
        solution_cards = list(self.solution.values())
        self.pool = [card for card in self.all_clues if card not in solution_cards]
        random.shuffle(self.pool)

    def add_log(self, sender, text, tag="SYSTEM"):
        """Pushes event logs and visual conversational updates to the screen."""
        if tag == "SYSTEM":
            self.game_log.append(f"[SYS] {text}")
        elif tag == "EXTERNAL":
            self.game_log.append(f"[{sender}]: \"{text}\"")
        elif tag == "DISCOVERY":
            self.game_log.append(f"[★] {text}")

    def distribute_clues(self):
        """Uniformly distributes cards to player hands."""
        if not self.players:
            return
        for idx, card in enumerate(self.pool):
            self.players[idx % len(self.players)].hand.append(card)
        self.add_log("SYSTEM", "The confidential cards have been dealt.")

    def get_room_at_coords(self, coords):
        for name, data in self.rooms.items():
            if coords in data["coords"]:
                return name
        return None

    def get_valid_moves(self, start_coords, roll=3):
        valid_targets = []
        queue = [(start_coords, 0)]
        visited = {start_coords}
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
                
                if 0 <= nx < 11 and 0 <= ny < 11:
                    if neighbor in visited or neighbor in player_positions:
                        continue
                    
                    room_at_neighbor = self.get_room_at_coords(neighbor)
                    if room_at_neighbor is None:
                        visited.add(neighbor)
                        queue.append((neighbor, dist + 1))
                    else:
                        door_coords = self.rooms[room_at_neighbor]["door"]
                        if curr == door_coords or neighbor == door_coords:
                            visited.add(neighbor)
                            queue.append((neighbor, dist + 1))
                            
        return list(set(valid_targets))

    def render_view(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        grid = [["." for _ in range(11)] for _ in range(11)]
        
        for r_name, r_data in self.rooms.items():
            first_coord = r_data["coords"][0]
            grid[first_coord[0]][first_coord[1]] = r_data["char"]
            for cx, cy in r_data["coords"]:
                if grid[cx][cy] == ".":
                    grid[cx][cy] = "x"
            dx, dy = r_data["door"]
            grid[dx][dy] = "d"

        for p in self.players:
            px, py = p.coords
            grid[px][py] = p.token

        print("====================== CLUE SIMULATION BOARD ======================")
        print(" Map Representation                                 Game Event Log")
        print("-------------------------------------------------------------------")
        
        log_start = max(0, len(self.game_log) - 15)
        visible_logs = self.game_log[log_start:]
        
        for r in range(11):
            map_row = " ".join(grid[r])
            log_row = visible_logs[r] if r < len(visible_logs) else ""
            print(f"  {map_row}   │  {log_row}")
            
        print("-------------------------------------------------------------------")
        print(" R=Scarlet, M=Mustard, W=White, G=Green, P=Peacock, U=Plum | d=Door")
        print("===================================================================")

class Player:
    def __init__(self, name, token, start_coords, is_human=False, ai_type=None):
        self.name = name
        self.token = token
        self.coords = start_coords
        self.hand = []
        self.is_human = is_human
        self.ai_type = ai_type

def bootstrap_all_directories():
    directories = ["miss_scarlet", "colonel_mustard", "mrs_white", "mr_green", "mrs_peacock", "professor_plum"]
    for folder in directories:
        os.makedirs(folder, exist_ok=True)
        init_file = os.path.join(folder, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w") as f:
                f.write("")

def run_simulation():
    bootstrap_all_directories()
    
    global ClueAIBridge
    if ClueAIBridge is None:
        try:
            from clue_ai_bridge import ClueAIBridge
        except ImportError:
            pass

    game = ClueGame()
    
    os.system('cls' if os.name == 'nt' else 'clear')
    print("===================================================================")
    print("              COMPLETE 6-LLM CLUE SOCIAL SIMULATOR                ")
    print("===================================================================")
    print("Choose Simulation Type:")
    print("  [1] Spectator Mode  -> Watch all 6 LLM agents play and scheme.")
    print("  [2] Active Play     -> Control Miss Scarlet alongside 5 LLMs.")
    print("-------------------------------------------------------------------")
    
    mode_selection = input("Select Option [1-2, Default: 1]: ").strip() or "1"
    
    try:
        pace = float(input("\nConfigure Turn Pace (seconds) [Default: 3.5]: ").strip() or "3.5")
    except ValueError:
        pace = 3.5
        
    if mode_selection == "2":
        p1 = Player("Miss Scarlet", "R", (3, 1), is_human=True)
    else:
        p1 = Player("Miss Scarlet", "R", (3, 1), is_human=False, ai_type="miss_scarlet")
        
    p2 = Player("Colonel Mustard", "M", (1, 7), is_human=False, ai_type="colonel_mustard")
    p3 = Player("Mrs. White", "W", (7, 1), is_human=False, ai_type="mrs_white")
    p4 = Player("Mr. Green", "G", (9, 3), is_human=False, ai_type="mr_green")
    p5 = Player("Mrs. Peacock", "P", (7, 9), is_human=False, ai_type="mrs_peacock")
    p6 = Player("Professor Plum", "U", (3, 9), is_human=False, ai_type="professor_plum")
    
    game.players = [p1, p2, p3, p4, p5, p6]
    game.distribute_clues()
    
    turn_counter = 0
    max_turns = 150
    
    while turn_counter < max_turns:
        for player in game.players:
            game.render_view()
            
            if player.is_human:
                print(f"\n★ [YOUR TURN - {player.name}] ★")
                print(f"Your Secret Hand: {player.hand}")
                roll = random.randint(2, 4)
                print(f"You rolled: {roll}")
                
                valid_moves = game.get_valid_moves(player.coords, roll)
                print("Options: [1] Move, [2] Speak, [3] Suggest, [4] Accuse, [5] Quit")
                choice = input("Choice: ").strip()
                
                if choice == "1":
                    print("\nSelect coordinate path:")
                    for idx, m in enumerate(valid_moves):
                        room_label = game.get_room_at_coords(m)
                        label = f"Room: {room_label}" if room_label else "Hallway"
                        print(f"  [{idx}] Coordinate: {m} ({label})")
                    try:
                        move_idx = int(input("Index: ").strip())
                        if 0 <= move_idx < len(valid_moves):
                            player.coords = valid_moves[move_idx]
                            room_label = game.get_room_at_coords(player.coords)
                            if room_label:
                                game.add_log(player.name, f"Entered Room: {room_label}", tag="SYSTEM")
                            else:
                                game.add_log(player.name, f"Traversed hallway to {player.coords}", tag="SYSTEM")
                    except Exception:
                        pass
                elif choice == "2":
                    msg = input("Type chat speech: ")
                    game.add_log(player.name, msg, tag="EXTERNAL")
                elif choice == "3":
                    room = game.get_room_at_coords(player.coords)
                    if not room:
                        print("Must be in a room!")
                        time.sleep(1)
                        continue
                    w = input("Weapon: ").strip()
                    s = input("Suspect: ").strip()
                    game.add_log("SYSTEM", f"{player.name} suggests: {s} with {w} in the {room}")
                    time.sleep(1.5)
                elif choice == "4":
                    r = input("Room: ").strip()
                    w = input("Weapon: ").strip()
                    s = input("Suspect: ").strip()
                    if r == game.solution["room"] and w == game.solution["weapon"] and s == game.solution["suspect"]:
                        game.add_log("SYSTEM", f"VICTORY! {player.name} solved the crime!", tag="DISCOVERY")
                        sys.exit(0)
                    else:
                        game.add_log("SYSTEM", f"FAIL! {player.name}'s accusation was wrong.")
                elif choice == "5":
                    sys.exit(0)
            else:
                if ClueAIBridge is not None:
                    game_over = ClueAIBridge.execute_agent_turn(game, player)
                    if game_over:
                        game.render_view()
                        print("\nSimulation completed!")
                        sys.exit(0)
                    time.sleep(pace)
            
        turn_counter += 1

if __name__ == "__main__":
    run_simulation()