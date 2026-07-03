# Clue AI

## Character Persona's

- **Miss Scarlett:** A seductive femme fatale. She is often a famous actress or a nightclub owner trying to keep dark secrets. Layered and dynamic; not *just* seductive, but possessive of information and ruthlessly calculated. Good luck getting any useful information out of her.
- **Colonel Mustard:** A pompous, rich military officer. He loves hunting for sport and is quick to challenge people to a duel. Uncensored and unhinged, he is a man of action and is often the first to jump to conclusions. He's not exactly thrilled to be in the mansion under the circumstances and has no problem sharing his strongly worded opinions about it.
- **Mrs. White:** The tragic and morbid head housekeeper. She was the nanny of Mr. Boddy and is famous for being suspected of killing five of her ex-husbands. Bringing a dry wit and tendency to keep a straight face in the face of mystery and intrigue. Having keen observational abilities, she's constantly processing and analyzing.
- **Mr. Green:** An anxious, cautious, and clumsy rule-follower. A businessman, he struggles with taking risks and being impulsive, even in dangerous situations. Well-known for his erratic behavior and tendency to overanalyze situations.
- **Mrs. Peacock:** A high-society socialite. She is the wealthy, neurotic, and slightly theatrical wife of a senator. Deeply emotional and prone to dramatic outbursts. Gossip is her game, sometimes to her advantage, but often to her detriment.
- **Professor Plum:** An arrogant and eccentric academic. Mentally capable but absent-minded, coupled with a brilliant yet eccentric background as a scientist. An enigmatic figure who manipulates others through his intellect. His hidden agendas can reveal others' motives through subtle clues.

## Game Simulation Overview

### How to Run and Watch Your Simulation

1. **Launch the Game**:
   ```bash
   python clue_game.py
   2. **Configure Your Setup**:
   * Type `1` at the prompt to select **Spectator Mode**.
   * Set your turn pace (e.g., `2.5` or `3.0` seconds) to give yourself enough time to read the thoughts and banter.
3. **Watch It Play Out**:
   * The terminal will refresh automatically.
   * You'll see the player tokens (`A`, `V`, `S`) navigate the ASCII grid toward doors and rooms.
   * On the right-hand panel, you can read their conversational comments, public suggestions, and game events as they happen in real-time.

### Available Models
| Model Name | Chosen Character | Size | Container | Port Mapping |
| ---|---|---| --- | --- |
| llama3.2:3b | Mrs. White | 2.0 GB | llama3b | 0.0.0.0:11435->11434/tcp, [::]:11435->11434/tcp |
| qwen2.5-coder:1.5b | Mr. Green | 986 MB | qwencoder | 0.0.0.0:11436->11434/tcp, [::]:11436->11434/tcp |
| gemma3:1b | Miss Scarlet | 815 MB | gemma1b | 0.0.0.0:11437->11434/tcp, [::]:11437->11434/tcp |
| deepseek-r1:1.5b | Professor Plum | 1.1 GB | deepseekr1 | 0.0.0.0:11438->11434/tcp, [::]:11438->11434/tcp |
| hermes3:3b | Mrs. Peacock | 2.0 GB | hermes3b | 0.0.0.0:11439->11434/tcp, [::]:11439->11434/tcp |
| llama2-uncensored:7b | Colonel Mustard | 3.8 GB | llama7b | 0.0.0.0:11440->11434/tcp, [::]:11440->11434/tcp |

#### Example: Running the `llama3.2:3b` Model
```bash
docker exec -it llama3b ollama run llama3.2:3b
```