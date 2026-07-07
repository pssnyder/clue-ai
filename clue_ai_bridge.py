import importlib
import inspect
import random


class ClueAIBridge:
    PERSONA_LIBRARY = {
        "Miss Scarlet": {
            "name": "Miss Scarlet",
            "description": "A seductive, dramatic, and manipulative socialite who wants to dominate the room and control the narrative.",
            "voice": "flirty, sharp, and theatrical"
        },
        "Colonel Mustard": {
            "name": "Colonel Mustard",
            "description": "A pompous, military-minded opportunist who speaks bluntly and jumps to bold conclusions.",
            "voice": "boastful, impatient, and combative"
        },
        "Mrs. White": {
            "name": "Mrs. White",
            "description": "The tragic, morbid, dry-witted head housekeeper who speaks with deadpan humor and keen observation.",
            "voice": "deadpan, wry, and quietly grim"
        },
        "Mr. Green": {
            "name": "Mr. Green",
            "description": "An anxious, cautious rule-follower who overthinks every decision and worries about consequences.",
            "voice": "nervous, polite, and hesitant"
        },
        "Mrs. Peacock": {
            "name": "Mrs. Peacock",
            "description": "A high-society socialite who is theatrical, emotional, and deeply interested in gossip and appearances.",
            "voice": "dramatic, gossip-driven, and theatrical"
        },
        "Professor Plum": {
            "name": "Professor Plum",
            "description": "An arrogant academic with a brilliant mind and a subtly manipulative, eccentric edge.",
            "voice": "aloof, cerebral, and smug"
        },
    }

    @staticmethod
    def get_persona(player):
        persona_name = getattr(player, "name", None)
        persona = ClueAIBridge.PERSONA_LIBRARY.get(persona_name)
        if persona:
            return persona

        return {
            "name": persona_name or "Unknown Character",
            "description": "A thoughtful and strategic player in Clue.",
            "voice": "measured and observant"
        }

    @staticmethod
    def construct_observation(game, current_player):
        """Translates current board coordinates and game elements to JSON observation logs."""
        current_room = game.get_room_at_coords(current_player.coords)
        roll_value = random.randint(2, 4)
        valid_moves = game.get_valid_moves(current_player.coords, roll_value)
        persona = ClueAIBridge.get_persona(current_player)
        
        return {
            "player_info": {
                "name": current_player.name,
                "token": current_player.token,
                "position": current_player.coords,
                "current_room": current_room,
                "hand": current_player.hand,
                "valid_coordinate_moves": valid_moves,
                "movement_roll": roll_value,
                "persona_name": persona["name"],
                "persona_description": persona["description"],
                "persona_voice": persona.get("voice", "")
            },
            "board_map": {
                "rooms": {r: d["coords"] for r, d in game.rooms.items()},
                "doors": {r: d["door"] for r, d in game.rooms.items()}
            },
            "other_players": [
                {"name": p.name, "token": p.token, "position": p.coords, "room": game.get_room_at_coords(p.coords)}
                for p in game.players if p.name != current_player.name
            ],
            "public_history": list(game.game_log[-15:]),
            "valid_options": {
                "rooms": game.room_names,
                "weapons": game.weapons,
                "suspects": game.suspects
            }
        }

    @staticmethod
    def execute_agent_turn(game, player):
        """Routes observation objects dynamically to individual package agents."""
        observation = ClueAIBridge.construct_observation(game, player)
        
        try:
            module_name = f"{player.ai_type}.agent"
            agent_module = importlib.import_module(module_name)
        except ImportError:
            game.add_log("SYSTEM", f"Agent path loading failed for: {player.ai_type}")
            return False

        try:
            agent_class = getattr(agent_module, "ClueAgent")
            persona = ClueAIBridge.get_persona(player)
            init_signature = inspect.signature(agent_class.__init__)
            init_params = init_signature.parameters
            if "persona" in init_params:
                agent_instance = agent_class(player.name, persona=persona)
            else:
                agent_instance = agent_class(player.name)
        except Exception as e:
            game.add_log("SYSTEM", f"Failed to instantiate {player.name}: {e}")
            return False

        decision = agent_instance.take_action(observation)
        
        # Log internal monologue securely to file
        if "internal_thought" in decision and decision["internal_thought"]:
            try:
                with open("agent_internal_thoughts.log", "a", encoding="utf-8") as file:
                    file.write(f"[{player.name} Thoughts]: {decision['internal_thought']}\n")
            except IOError:
                pass

        if "external_thought" in decision and decision["external_thought"]:
            game.add_log(player.name, decision["external_thought"], tag="EXTERNAL")
            game.render_view()

        action_type = decision.get("action_type", "MOVE").upper()
        
        if action_type == "MOVE":
            target_coords = decision.get("move_target", player.coords)
            if isinstance(target_coords, list):
                target_coords = tuple(target_coords)
                
            player.coords = target_coords
            room_name = game.get_room_at_coords(player.coords)
            if room_name:
                game.add_log("SYSTEM", f"{player.name} moved into: {room_name}")
            else:
                game.add_log("SYSTEM", f"{player.name} walked onto hallway space {player.coords}")
                
        elif action_type == "SUGGEST":
            sugg = decision.get("suggestion", {})
            room = sugg.get("room")
            weapon = sugg.get("weapon")
            suspect = sugg.get("suspect")
            
            game.add_log("SYSTEM", f"{player.name} suggests: {suspect} with the {weapon} in the {room}")
            
            if (room == game.solution["room"] and 
                weapon == game.solution["weapon"] and 
                suspect == game.solution["suspect"]):
                game.add_log("SYSTEM", "The suggestion matches the secret parameters!", tag="DISCOVERY")
            else:
                game.add_log("SYSTEM", "The suggestion was disproved.")
                
        elif action_type == "ACCUSE":
            acc = decision.get("accusation", {})
            room = acc.get("room")
            weapon = acc.get("weapon")
            suspect = acc.get("suspect")
            
            game.add_log("SYSTEM", f"🚨 {player.name} ACCUSES: {suspect} in the {room} with the {weapon}! 🚨")
            
            if (room == game.solution["room"] and 
                weapon == game.solution["weapon"] and 
                suspect == game.solution["suspect"]):
                game.add_log("SYSTEM", f"🎯 VICTORY! {player.name} solved the murder!", tag="DISCOVERY")
                return True
            else:
                game.add_log("SYSTEM", f"❌ FAILURE! {player.name}'s accusation was wrong.")
                
        return False