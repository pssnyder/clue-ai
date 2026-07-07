import json
import random
import requests

class ClueAgent:
    def __init__(self, name, persona=None):
        self.name = name
        self.host_address = "192.168.50.220:11434"
        self.model_identifier = "qwen2.5-coder:7b"
        self.notepad = {"rooms": {}, "weapons": {}, "suspects": {}}
        self.persona = persona or {
            "name": "Mrs. White",
            "description": "The tragic, morbid, dry-witted head housekeeper who speaks with deadpan humor and keen observation.",
            "voice": "deadpan, wry, and quietly grim"
        }

    def initialize_notepad(self, observation):
        valid = observation["valid_options"]
        my_hand = observation["player_info"]["hand"]
        for r in valid["rooms"]:
            self.notepad["rooms"][r] = "HELD" if r in my_hand else "UNKNOWN"
        for w in valid["weapons"]:
            self.notepad["weapons"][w] = "HELD" if w in my_hand else "UNKNOWN"
        for s in valid["suspects"]:
            self.notepad["suspects"][s] = "HELD" if s in my_hand else "UNKNOWN"

    def query_local_llm(self, prompt):
        endpoint = f"http://{self.host_address}/api/generate"
        payload = {
            "model": self.model_identifier,
            "prompt": prompt,
            "format": "json",
            "stream": False
        }
        try:
            response = requests.post(endpoint, json=payload, timeout=5.0)
            response.raise_for_status()
            return json.loads(response.json().get("response", "{}"))
        except Exception:
            return None

    def get_deductive_fallback(self, observation):
        unknown_suspects = [s for s, status in self.notepad["suspects"].items() if status == "UNKNOWN"]
        unknown_weapons = [w for w, status in self.notepad["weapons"].items() if status == "UNKNOWN"]
        unknown_rooms = [r for r, status in self.notepad["rooms"].items() if status == "UNKNOWN"]
        
        current_room = observation["player_info"]["current_room"]
        if current_room and current_room in unknown_rooms:
            s_s = random.choice(unknown_suspects) if unknown_suspects else "Miss Scarlet"
            s_w = random.choice(unknown_weapons) if unknown_weapons else "Dagger"
            return {
                "internal_thought": "Querying room properties to gather missing facts.",
                "external_thought": f"I suggest it was {s_s} in the {current_room} with the {s_w}!",
                "action_type": "SUGGEST",
                "suggestion": {"suspect": s_s, "weapon": s_w, "room": current_room}
            }
            
        valid_moves = observation["player_info"]["valid_coordinate_moves"]
        chosen = random.choice(valid_moves) if valid_moves else observation["player_info"]["position"]
        return {
            "internal_thought": "Traversing grid hallway coordinates safely.",
            "external_thought": "Searching the hallway corridors.",
            "action_type": "MOVE",
            "move_target": chosen
        }

    def take_action(self, observation):
        if not self.notepad["rooms"]:
            self.initialize_notepad(observation)
            
        unknown_suspects = [s for s, status in self.notepad["suspects"].items() if status == "UNKNOWN"]
        unknown_weapons = [w for w, status in self.notepad["weapons"].items() if status == "UNKNOWN"]
        unknown_rooms = [r for r, status in self.notepad["rooms"].items() if status == "UNKNOWN"]
        valid_moves = observation["player_info"]["valid_coordinate_moves"]
        current_room = observation["player_info"]["current_room"]
        
        persona_name = observation["player_info"].get("persona_name", self.persona["name"])
        persona_description = observation["player_info"].get("persona_description", self.persona["description"])
        persona_voice = observation["player_info"].get("persona_voice", self.persona.get("voice", ""))

        system_instructions = f"""
        You are {persona_name} in a game of Clue.
        
        Persona:
        - {persona_description}
        - Speak in a {persona_voice} voice.
        - Keep the character consistent even when the situation is tense or absurd.
        
        Game State:
        - Your secret Hand: {observation['player_info']['hand']}
        - Current room: {current_room}
        - Uneliminated Suspects: {unknown_suspects}
        - Uneliminated Weapons: {unknown_weapons}
        - Uneliminated Rooms: {unknown_rooms}
        - Valid move coordinates: {valid_moves}
        
        Actions:
        1. MOVE: Choose from {valid_moves}.
        2. SUGGEST: Use current room: "{current_room}". Choose weapon from {unknown_weapons} and suspect from {unknown_suspects}.
        3. ACCUSE: If you have eliminated down to 1 suspect, 1 weapon, and 1 room.
        
        Respond ONLY with a valid JSON block of this schema:
        {{
            "internal_thought": "Strategic reasoning.",
            "external_thought": "Banter said out loud reflecting your dark, morbid housekeeping wit.",
            "action_type": "MOVE" | "SUGGEST" | "ACCUSE",
            "move_target": [x, y],
            "suggestion": {{"suspect": "Name", "weapon": "Name", "room": "Name"}},
            "accusation": {{"suspect": "Name", "weapon": "Name", "room": "Name"}}
        }}
        """
        decision = self.query_local_llm(system_instructions)
        if not decision or not isinstance(decision, dict):
            return self.get_deductive_fallback(observation)
            
        action_type = decision.get("action_type", "MOVE").upper()
        if action_type == "MOVE":
            move_target = decision.get("move_target")
            if isinstance(move_target, list):
                move_target = tuple(move_target)
            if move_target not in [tuple(m) for m in valid_moves]:
                decision["move_target"] = random.choice(valid_moves) if valid_moves else observation["player_info"]["position"]
                
        return decision