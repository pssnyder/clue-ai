import json
import random
import re
import requests

class ClueAgent:
    def __init__(self, name):
        self.name = name
        self.host_address = "192.168.50.220:11438"
        self.model_identifier = "deepseek-r1:1.5b"
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

    def query_local_llm_with_think_parsing(self, prompt):
        endpoint = f"http://{self.host_address}/api/generate"
        payload = {
            "model": self.model_identifier,
            "prompt": prompt,
            "stream": False
        }
        try:
            response = requests.post(endpoint, json=payload, timeout=8.0)
            response.raise_for_status()
            raw_text = response.json().get("response", "{}")
            
            internal_thought = ""
            think_match = re.search(r'<think>(.*?)</think>', raw_text, flags=re.DOTALL)
            if think_match:
                internal_thought = think_match.group(1).strip()
                # Clean block entirely from final payload
                raw_text = re.sub(r'<think>.*?</think>', '', raw_text, flags=re.DOTALL).strip()
            
            # Sanitize any stray JSON formatting wrappers
            if raw_text.startswith("```json"):
                raw_text = raw_text.replace("```json", "").replace("```", "").strip()
            elif raw_text.startswith("```"):
                raw_text = raw_text.replace("```", "").strip()
                
            decision = json.loads(raw_text)
            if isinstance(decision, dict):
                # Inject parsed thinking tokens as the official internal thoughts
                if internal_thought:
                    decision["internal_thought"] = f"[DeepSeek COT]: {internal_thought}"
                return decision
        except Exception:
            return None
        return None

    def get_deductive_fallback(self, observation):
        unknown_suspects = [s for s, status in self.notepad["suspects"].items() if status == "UNKNOWN"]
        unknown_weapons = [w for w, status in self.notepad["weapons"].items() if status == "UNKNOWN"]
        unknown_rooms = [r for r, status in self.notepad["rooms"].items() if status == "UNKNOWN"]
        
        current_room = observation["player_info"]["current_room"]
        if current_room and current_room in unknown_rooms:
            s_s = random.choice(unknown_suspects) if unknown_suspects else "Miss Scarlet"
            s_w = random.choice(unknown_weapons) if unknown_weapons else "Revolver"
            return {
                "internal_thought": "Failed DeepSeek extraction. Defaulting to deductive suggestion.",
                "external_thought": f"Purely scientific hypothesis: {s_s} with the {s_w} in the {current_room}.",
                "action_type": "SUGGEST",
                "suggestion": {"suspect": s_s, "weapon": s_w, "room": current_room}
            }
            
        valid_moves = observation["player_info"]["valid_coordinate_moves"]
        chosen = random.choice(valid_moves) if valid_moves else observation["player_info"]["position"]
        return {
            "internal_thought": "Failed parse of R1 response payload. Fallback coordinates assigned.",
            "external_thought": "Analyzing the geometric pathing options.",
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
        You are Professor Plum in a game of Clue.
        
        Persona:
        - You are a highly intellectual, arrogant, and pedantic academic.
        - You analyze facts with clinical precision, often showing condescension toward other players.
        
        Game Information:
        - Hand: {observation['player_info']['hand']}
        - Room: {current_room}
        - Uneliminated Suspects: {unknown_suspects}
        - Uneliminated Weapons: {unknown_weapons}
        - Uneliminated Rooms: {unknown_rooms}
        - Valid Move coordinates: {valid_moves}
        
        Provide your reasoning inside <think></think> tags.
        Then, output the final action as a valid JSON block of this schema:
        {{
            "internal_thought": "Calculative reasoning.",
            "external_thought": "Arrogant, scholarly academic banter to say out loud.",
            "action_type": "MOVE" | "SUGGEST" | "ACCUSE",
            "move_target": [x, y],
            "suggestion": {{"suspect": "Name", "weapon": "Name", "room": "Name"}},
            "accusation": {{"suspect": "Name", "weapon": "Name", "room": "Name"}}
        }}
        """
        decision = self.query_local_llm_with_think_parsing(system_instructions)
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