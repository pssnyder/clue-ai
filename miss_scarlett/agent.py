import json
import random
import requests

class ClueAgent:
    def __init__(self, name):
        self.name = name
        self.host_address = "192.168.50.220:11437"
        self.model_identifier = "gemma3:1b"
        self.notepad = {"rooms": {}, "weapons": {}, "suspects": {}}

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
            s_s = random.choice(unknown_suspects) if unknown_suspects else "Colonel Mustard"
            s_w = random.choice(unknown_weapons) if unknown_weapons else "Candlestick"
            return {
                "internal_thought": "Scarlet logic: testing nearby suspects.",
                "external_thought": f"Do tell, could it be {s_s} right here with the {s_w}?",
                "action_type": "SUGGEST",
                "suggestion": {"suspect": s_s, "weapon": s_w, "room": current_room}
            }
            
        valid_moves = observation["player_info"]["valid_coordinate_moves"]
        chosen = random.choice(valid_moves) if valid_moves else observation["player_info"]["position"]
        return {
            "internal_thought": "Gemma model fallback walking.",
            "external_thought": "I must keep moving, darlings.",
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
        
        system_instructions = f"""
        You are Miss Scarlet in Clue.
        
        Persona:
        - Flirty, dramatic, manipulative, and deeply ambitious. Always wants to be center stage.
        
        Game Information:
        - Hand: {observation['player_info']['hand']}
        - Room: {current_room}
        - Suspects: {unknown_suspects}
        - Weapons: {unknown_weapons}
        - Valid Move coordinates: {valid_moves}
        
        Output JSON only:
        {{
            "internal_thought": "Strategy.",
            "external_thought": "Flirty, manipulative banter said out loud.",
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