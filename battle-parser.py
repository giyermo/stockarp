import json

def count_turns(log):
    turn_count = 0
    for line in log.split('\n'):
        if line.startswith('|turn|'):
            turn_count += 1
    return turn_count


class Pokemon:
    def __init__(self, species, level, gender, current_hp, max_hp):
        self.species = species
        self.level = level
        self.gender = gender
        self.current_hp = current_hp
        self.max_hp = max_hp
        self.known_moves = set()  # Track known moves

    def update_hp(self, new_hp):
        self.current_hp = new_hp

    def add_move(self, move):
        self.known_moves.add(move)



    def __repr__(self):
        return f"{self.species} (Lv.{self.level}, HP: {self.current_hp}/{self.max_hp})"


class BattleLogParser:
    def __init__(self):
        self.teams = {'p1a': {}, 'p2a': {}}  # Stores all Pokémon
        self.active = {'p1a': None, 'p2a': None}  # Active Pokémon
        self.turn_count = 0

    def get_pokemon(self, player_id, pokemon_species, *details):
        """Get or create Pokémon"""
        if pokemon_species not in self.teams[player_id]:
            level, gender, current_hp, max_hp = details
            self.teams[player_id][pokemon_species] = Pokemon(pokemon_species, level, gender, current_hp, max_hp)
            # print(f"New pokemon added: {pokemon_species}")

        elif details != ():
            level, gender, current_hp, max_hp = details
            self.teams[player_id][pokemon_species].update_hp(current_hp)

        return self.teams[player_id][pokemon_species]

    def parse_log(self, log_content):
        """Main parsing method"""
        for line in log_content.split('\n'):
            if line.startswith('|turn|'):
                self.turn_count += 1


            parts = line.strip().split('|')
            if len(parts) < 2: continue

            event_type = parts[1].strip()

            if event_type == 'switch':
                self.handle_switch(parts)
            elif event_type == 'move':
                self.handle_move(parts)

    def handle_switch(self, parts):
        """Handle switch/drag events"""
        if len(parts) < 4: return
        player_id = parts[2].split(':')[0].strip()
        if len(player_id) == 2:
            player_id += "a" # TODO
        pokemon_species = parts[2].split(':')[1].strip()
        details = [x.strip() for x in parts[3].split(",")]
        level = details[1][1:]
        if len(details) > 2:
            gender = details[2]
        else:
            gender = None

        hp_str = parts[4]
        current_hp, max_hp = hp_str.split("/")

        pokemon = self.get_pokemon(player_id, pokemon_species, level, gender, current_hp, max_hp)

        print("Turn", self.turn_count, pokemon, "switches in")


    def handle_move(self, parts):
        """Handle move usage"""
        if len(parts) < 4: return

        player_id = parts[2].split(':')[0].strip()
        if len(player_id) == 2:
            player_id += "a" # TODO

        pokemon_species = parts[2].split(':')[1].strip()
        move_name = parts[3].strip()

        pokemon = self.get_pokemon(player_id, pokemon_species)
        pokemon.add_move(move_name)

        affected_player_id = parts[4].split(':')[0].strip()
        if len(affected_player_id) == 2:
            affected_player_id += "a" # TODO

        affected_pokemon_species = parts[4].split(':')[1].strip()

        affected_pokemon = self.get_pokemon(affected_player_id, affected_pokemon_species)

        print("Turn", self.turn_count, pokemon, "uses", move_name, "into", affected_pokemon)



# Test with a sample log
with open("replays_gen9randombattle/gen9randombattle-2152949532.json", "r") as f:
    sample_log = json.load(f)["log"]


def test_parser():
    test_log = sample_log

    # Create and run parser
    parser = BattleLogParser()
    parser.parse_log(test_log)


test_parser()