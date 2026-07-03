import random

class ClueAgent:
    def __init__(self, name):
        self.name = name
        # Notepad to track cards and eliminate possibilities
        self.notepad = {
            "rooms": {},
            "weapons": {},
            "suspects": {}
        }

    def initialize_notepad(self, observation):
        """Initializes the notepad, marking off cards in hand as eliminated."""
        valid = observation["valid_options"]
        my_hand = observation["player_info"]["hand"]
        
        for r in valid["rooms"]:
            self.notepad["rooms"][r] = "HELD" if r in my_hand else "UNKNOWN"
        for w in valid["weapons"]:
            self.notepad["weapons"][w] = "HELD" if w in my_hand else "UNKNOWN"
        for s in valid["suspects"]:
            self.notepad["suspects"][s] = "HELD" if s in my_hand else "UNKNOWN"

    def update_notepad_from_logs(self, history):
        """Analyzes public game logs to logically cross out elements."""
        for log in history:
            # If the log contains information showing a fact has been disproved
            if "checked and disproved" in log or "did not solve the mystery" in log:
                # We can deduce patterns over multiple turns here
                pass

    def take_action(self, observation):
        """Executes reasoning logic to move, suggest, or accuse."""
        if not self.notepad["rooms"]:
            self.initialize_notepad(observation)
            
        self.update_notepad_from_logs(observation["public_history"])
        
        # Gather all candidates we haven't eliminated yet
        unknown_suspects = [s for s, status in self.notepad["suspects"].items() if status == "UNKNOWN"]
        unknown_weapons = [w for w, status in self.notepad["weapons"].items() if status == "UNKNOWN"]
        unknown_rooms = [r for r, status in self.notepad["rooms"].items() if status == "UNKNOWN"]
        
        # Check if the solution is completely solved (only 1 unknown left for each category)
        if len(unknown_suspects) == 1 and len(unknown_weapons) == 1 and len(unknown_rooms) == 1:
            acc_suspect = unknown_suspects[0]
            acc_weapon = unknown_weapons[0]
            acc_room = unknown_rooms[0]
            return {
                "internal_thought": f"Perfect mathematical logical path! Eliminating down to suspect={acc_suspect}, weapon={acc_weapon}, room={acc_room}.",
                "external_thought": "My deductions are complete. I have formulated an accusation!",
                "action_type": "ACCUSE",
                "accusation": {"suspect": acc_suspect, "weapon": acc_weapon, "room": acc_room}
            }
            
        # Normal play cycle: Make a suggestion if inside a room we haven't eliminated
        current_room = observation["player_info"]["current_room"]
        
        if current_room and current_room in unknown_rooms:
            sug_suspect = random.choice(unknown_suspects) if unknown_suspects else "Miss Scarlet"
            sug_weapon = random.choice(unknown_weapons) if unknown_weapons else "Dagger"
            
            # The agent will update its own notepad since it is testing this suggestion
            # A smart agent might eliminate these when proven wrong
            return {
                "internal_thought": f"I need to query {sug_suspect} and the {sug_weapon} in the {current_room} to cross-reference my notebook.",
                "external_thought": f"Based on tracking data, I suggest it was {sug_suspect} in the {current_room} with the {sug_weapon}!",
                "action_type": "SUGGEST",
                "suggestion": {"suspect": sug_suspect, "weapon": sug_weapon, "room": current_room}
            }
        
        # If in a hallway or already eliminated room, move towards an uneliminated room door
        valid_coordinates = observation["player_info"]["valid_coordinate_moves"]
        chosen_coord = observation["player_info"]["position"]
        
        if valid_coordinates:
            # Score target tiles: Prefer coordinates that are closer to doors of uneliminated rooms
            best_coord = random.choice(valid_coordinates)
            min_dist = 999
            
            for room in unknown_rooms:
                door_coord = observation["board_map"]["doors"].get(room)
                if door_coord:
                    # Manhattan distance heuristic to find the nearest door
                    for coord in valid_coordinates:
                        dist = abs(coord[0] - door_coord[0]) + abs(coord[1] - door_coord[1])
                        if dist < min_dist:
                            min_dist = dist
                            best_coord = coord
            chosen_coord = best_coord
        
        # Spatial Monologue thoughts
        internal_monologue = f"Moving to position {chosen_coord} tracking nearest doors to eliminate {unknown_rooms}."
        banter_options = [
            "Let's check the eastern hallways for evidence...",
            "Searching the corridors for traces...",
            "I'm keeping my eyes open on the movements of the others."
        ]
        
        return {
            "internal_thought": internal_monologue,
            "external_thought": random.choice(banter_options),
            "action_type": "MOVE",
            "move_target": chosen_coord
        }

# Remember to save and back up your work! 💾