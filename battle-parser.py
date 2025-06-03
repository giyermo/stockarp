import json

class Pokemon:
    def __init__(self, species, level, gender, current_hp, max_hp):
        self.species = species
        self.level = level
        self.gender = gender
        self.current_hp = current_hp
        self.max_hp = max_hp
        self.known_moves = set()  # Track known moves
        self.ability = None
        self.status = None
        self.fainted = False

    def update_hp(self, new_hp):
        difference = abs(int(self.current_hp) - int(new_hp))
        self.current_hp = new_hp

        return difference

    def add_move(self, move):
        self.known_moves.add(move)
        print(f"{self.species} knows {self.known_moves}")

    def update_ability(self, ability):
        self.ability = ability
        print(f"{self.species}'s ability is {self.ability}")

    def update_status(self, status):
        self.status = status
        print(f"{self.species} is now paralyzed")

    def faint(self):
        self.fainted = True
        print(self.species, "fainted")

    def __repr__(self):
        return f"{self.species} (Lv.{self.level}, HP: {self.current_hp}/{self.max_hp})"


class BattleLogParser:
    def __init__(self):
        self.teams = {'p1a': {}, 'p2a': {}}  # Stores all Pokémon
        self.active = {'p1a': None, 'p2a': None}  # Active Pokémon
        self.weather = "none"
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

            match event_type:
                case 'switch':
                    self.handle_switch(parts)
                case 'move':
                    self.handle_move(parts)
                case '-damage':
                    self.handle_damage(parts)
                case 'faint':
                    self.handle_faint(parts)
                case '-ability':
                    self.handle_ability(parts)
                case '-heal':
                    self.handle_heal(parts)
                case '-weather':
                    self.handle_weather(parts)
                case '-status':
                    self.handle_status(parts)

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

        self.active[player_id] = pokemon

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

        if parts[4] != '':
            affected_player_id = parts[4].split(':')[0].strip()
            if len(affected_player_id) == 2:
                affected_player_id += "a" # TODO

            affected_pokemon_species = parts[4].split(':')[1].strip()

            affected_pokemon = self.get_pokemon(affected_player_id, affected_pokemon_species)

            print("Turn", self.turn_count, pokemon, "uses", move_name, "into", affected_pokemon)

            if len(parts) > 5 and parts[5] == "[miss]":
                print("It missed!")

    def handle_damage(self, parts):
        """Handle damage being taken"""
        if len(parts) < 3: return

        player_id = parts[2].split(':')[0].strip()
        if len(player_id) == 2:
            player_id += "a"  # TODO

        pokemon_species = parts[2].split(':')[1].strip()

        if '/' in parts[3]:
            new_hp, hp_total = parts[3].split('/')
        elif 'fnt' in parts[3]:
            new_hp = 0
        else:
            raise EnvironmentError

        # TODO damage from things like life orb

        pokemon = self.get_pokemon(player_id, pokemon_species)
        damage = pokemon.update_hp(new_hp)

        print("Turn", self.turn_count, pokemon, "has taken", damage, "damage")

    def handle_faint(self, parts):
        """Handle pokemon fainting"""
        if len(parts) < 3: return

        player_id = parts[2].split(':')[0].strip()
        if len(player_id) == 2:
            player_id += "a"  # TODO

        pokemon_species = parts[2].split(':')[1].strip()

        pokemon = self.get_pokemon(player_id, pokemon_species)
        pokemon.faint()

    def handle_ability(self, parts):
        """Handle pokemon fainting"""
        if len(parts) < 3: return

        player_id = parts[2].split(':')[0].strip()
        if len(player_id) == 2:
            player_id += "a"  # TODO

        pokemon_species = parts[2].split(':')[1].strip()

        pokemon = self.get_pokemon(player_id, pokemon_species)
        pokemon.update_ability(parts[3])

    def handle_heal(self, parts):
        """Handle heal"""
        if len(parts) < 3: return

        player_id = parts[2].split(':')[0].strip()
        if len(player_id) == 2:
            player_id += "a"  # TODO

        pokemon_species = parts[2].split(':')[1].strip()

        if '/' in parts[3]:
            new_hp, hp_total = parts[3].split('/')
        elif 'fnt' in parts[3]:
            new_hp = 0
        else:
            raise EnvironmentError

        # TODO damage from things like life orb

        pokemon = self.get_pokemon(player_id, pokemon_species)
        damage = pokemon.update_hp(new_hp)

        print("Turn", self.turn_count, pokemon, "has healed", damage, "hp")

    def handle_weather(self, parts):
        """Handle weather"""
        if len(parts) < 3: return

        weather = parts[2].strip()

        self.weather = weather

        print("Weather is", weather)

    def handle_status(self, parts):
        """Handle status"""
        if len(parts) < 3: return

        player_id = parts[2].split(':')[0].strip()
        if len(player_id) == 2:
            player_id += "a"  # TODO

        pokemon_species = parts[2].split(':')[1].strip()

        status = parts[3]

        pokemon = self.get_pokemon(player_id, pokemon_species)
        pokemon.update_status(status)


# Test with a sample log
with open("replays_gen9randombattle/gen9randombattle-2152949532.json", "r") as f:
    sample_log = json.load(f)["log"]


def test_parser():
    test_log = sample_log

    # Create and run parser
    parser = BattleLogParser()
    parser.parse_log(test_log)

    print("---")


test_parser()