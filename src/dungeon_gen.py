import random, hashlib, json, time
from dataclasses import dataclass
from pathlib import Path

MAX_RETRY = 1000  # Nombre maximum de tentatives pour tout algo sur une grille (ex: placement de salle de boss, génération de chemins, etc.)
DATA_DIR = Path(__file__).resolve().parent


@dataclass
class RoomPattern:
    """Classe représentant un motif de salle."""

    pattern_id: str
    tier: int
    max_ennemy_slot: int
    containers: list[str]


class Room:
    room_type: str = "room"
    coord: tuple[int, int]
    population: list[str] = None
    pattern: RoomPattern | None = None

    def __init__(self, coord: tuple[int, int], room_type: str = "room") -> None:
        self.coord = coord
        self.room_type = room_type
        self.pattern = None

    def add_pattern(self, pattern: "RoomPattern") -> None:
        self.pattern = pattern


@dataclass
class LootTableItem:
    """Classe représentant un item dans une table de loot."""

    item_id: str
    rarity: float
    item_name: str
    item_description: str


class LootTable:
    """Classe représentant une table de loot."""

    def __init__(self, table_id: str, items: list[LootTableItem]) -> None:
        self.table_id: str = table_id
        self.items: list[LootTableItem] = items

    def get_random_item(self, rng: random.Random) -> LootTableItem:
        """Retourne un item aléatoire de la table en fonction de sa rareté."""
        total_rarity = sum(item.rarity for item in self.items)
        rand_value = rng.uniform(0, total_rarity)
        cumulative_rarity = 0.0
        for item in self.items:
            cumulative_rarity += item.rarity
            if rand_value <= cumulative_rarity:
                return item
        return self.items[-1]


@dataclass
class EnnemyTableItem:
    """Classe représentant un ennemi dans une table d'ennemis."""

    enemy_id: str
    rarity: float
    enemy_name: str
    enemy_description: str


class EnnemyTable:
    """Classe représentant une table d'ennemis."""

    def __init__(self, table_id: str, items: list[EnnemyTableItem]) -> None:
        self.table_id: str = table_id
        self.items: list[EnnemyTableItem] = items


def _loading_loot_tables() -> dict[str, LootTable]:
    with open(DATA_DIR / "loot_tables.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    loot_tables = {}
    for table_data in data:
        items = [LootTableItem(**item_data) for item_data in table_data["items"]]
        loot_table = LootTable(table_id=table_data["table_id"], items=items)
        loot_tables[table_data["table_id"]] = loot_table
    return loot_tables


def _loading_ennemy_tables() -> dict[str, EnnemyTable]:
    with open(DATA_DIR / "ennemy_tables.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    ennemy_tables = {}
    for table_data in data:
        items = [EnnemyTableItem(**item_data) for item_data in table_data["enemies"]]
        ennemy_table = EnnemyTable(table_id=table_data["table_id"], items=items)
        ennemy_tables[table_data["table_id"]] = ennemy_table
    return ennemy_tables


def _loading_room_patterns() -> list[RoomPattern]:
    with open(DATA_DIR / "room_patterns.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    room_patterns = [RoomPattern(**pattern_data) for pattern_data in data]
    return room_patterns


def manhattan_distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def derive_seed(master_seed: int, label: str) -> int:
    """Crée une liste de sous-seeds à partir d'une seed principale."""
    sub_seed_str: str = f"{master_seed}:{label}"

    sub_seed_hash: str = hashlib.sha256(sub_seed_str.encode("utf-8")).hexdigest()
    return int(sub_seed_hash[:16], 16)


def place_spawn_room(grid: list[tuple[int, int]], seed: int) -> Room:
    """Place la salle de spawn dans la grille."""
    spawn_sub_seed = derive_seed(seed, "spawn")
    rng = random.Random(spawn_sub_seed)
    grid_max_width = max(x for x, y in grid) + 1
    grid_max_height = max(y for x, y in grid) + 1

    # Choisir plus au centre de la grille pour la salle de spawn
    center_x, center_y = grid_max_width // 2, grid_max_height // 2
    grid.sort(key=lambda coord: manhattan_distance(coord, (center_x, center_y)))
    spawn_coord = rng.choices(
        grid,
        weights=[
            1 / (manhattan_distance(coord, (center_x, center_y)) + 1) ** 3
            for coord in grid
        ],
        k=1,
    )[0]
    return Room(coord=spawn_coord, room_type="spawn")


def place_boss_room(spawn_room, rooms, grid, visited, seed: int) -> Room | None:
    """Place la salle de boss dans la grille."""
    boss_sub_seed = derive_seed(seed, "boss")
    rng = random.Random(boss_sub_seed)

    raw_candidates = set()
    for room in rooms:
        x, y = room.coord
        neighbors = [(x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)]
        for neighbor in neighbors:
            if neighbor in grid and neighbor not in visited:
                raw_candidates.add(neighbor)
    raw_candidates.discard(spawn_room.coord)

    if not raw_candidates:
        return None

    # Filtre des case avec 1 seul voisin occupé pour une salle de boss en cul de sac
    candidates = [
        c for c in raw_candidates if number_of_occupied_neighbors(c, visited) == 1
    ]

    # Les trie de plus loin au plus proche de la salle de spawn et prend les 20% les plus éloignés
    sorted_by_far = sorted(
        candidates, key=lambda c: manhattan_distance(c, spawn_room.coord), reverse=True
    )
    candidates = sorted_by_far[: max(1, len(sorted_by_far) // 5)]

    boss_place = rng.choice(candidates)
    return Room(coord=boss_place, room_type="boss")


def split_budget(
    directions: list[str], total_budget: int, rng: random.Random
) -> dict[str, int]:
    """Répartit un budget total entre les directions disponibles"""
    direction_keys = directions

    raw_weights = {
        d: rng.uniform(0.7, 1.3) for d in direction_keys
    }  # Créé des poids aléatoires pour chaque direction
    total_weight = sum(raw_weights.values())

    # Répartit le budget total en fonction des poids normalisés
    budgets = {
        d: round(total_budget * w / total_weight) for d, w in raw_weights.items()
    }

    diff = total_budget - sum(budgets.values())
    if diff != 0:
        adjust_direction = rng.choice(direction_keys)
        budgets[adjust_direction] += diff

    return budgets


def maybe_drop_direction(
    available_directions: dict, rng: random.Random, drop_probability: float = 0.15
) -> dict:
    """Retires une direction selon une probabilité donnée, sauf si moins de 4 directions sont disponibles."""
    if len(available_directions) < 4:
        return available_directions

    if rng.random() < drop_probability:
        direction_to_drop = rng.choice(list(available_directions.keys()))
        return {d: c for d, c in available_directions.items() if d != direction_to_drop}

    return available_directions


def number_of_occupied_neighbors(
    coord: tuple[int, int], visited: set[tuple[int, int]]
) -> int:
    x, y = coord
    neighbors = [(x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)]
    return sum(
        1 for neighbor in neighbors if neighbor in visited
    )  # Somme des voisins occupés d'une case donnée


# fonction recursive qui trouve les voisins disponibles pour une coordonnée donnée
def find_available_neighbors(
    coord: tuple[int, int],
    rng: random.Random,
    grid: list[tuple[int, int]],
    visited: set[tuple[int, int]],
    step=1,
    path: list[tuple[int, int]] | None = None,
    previous_dir=None,
    continuity_bias: float = 0.5,
    attempts: int = 0,
) -> list[tuple[int, int]] | None:
    """Trouve les voisins disponibles pour une coordonnée donnée."""

    if step <= 0:  # Stop du récursif si le nombre d'étapes est atteint
        return path if path is not None else []

    if path is None:
        path = []

    x, y = coord
    directions = {
        (0, -1): (x, y - 1),
        (0, 1): (x, y + 1),
        (-1, 0): (x - 1, y),
        (1, 0): (x + 1, y),
    }

    directions = maybe_drop_direction(
        directions, rng, drop_probability=0.15
    )  # Retire une direction aléatoire avec une probabilité de 15%

    available = {
        d: n for d, n in directions.items() if n in grid and n not in visited
    }  # Filtre les voisins disponibles (dans la grille et non visités)
    if not available:
        if (
            attempts < MAX_RETRY
        ):  # Si aucun voisin disponible, on choisit une autre salle visitée aléatoirement pour continuer le chemin
            random_chosen_another_room = rng.choice(list(visited))
            return find_available_neighbors(
                random_chosen_another_room,
                rng,
                grid,
                visited,
                step,
                path,
                previous_dir=previous_dir,
                continuity_bias=continuity_bias,
                attempts=attempts + 1,
            )
        else:
            return path

    dirs = list(available.keys())
    if previous_dir in dirs:
        weights = [
            (
                continuity_bias
                if d == previous_dir
                else (1 - continuity_bias) / max(len(dirs) - 1, 1)
            )
            for d in dirs
        ]
    else:
        weights = [1] * len(dirs)  # pas de direction précédente valide -> uniforme

    chosen_dir = rng.choices(dirs, weights=weights, k=1)[0]
    chosen_neighbor = available[chosen_dir]

    visited.add(chosen_neighbor)
    path.append(chosen_neighbor)

    return find_available_neighbors(
        chosen_neighbor,
        rng,
        grid,
        visited,
        step - 1,
        path,
        previous_dir=chosen_dir,
        continuity_bias=continuity_bias,
    )


def apply_room_patterns(
    rooms: list[Room], room_patterns: list[RoomPattern], seed: int
) -> None:
    """Applique des motifs de salle aux salles générées."""
    room_seed = derive_seed(seed, "room_patterns")
    rng = random.Random(room_seed)
    for room in rooms:
        if room.room_type == "room":
            available_patterns = [
                pattern for pattern in room_patterns if pattern.tier == 1
            ]  # Exemple: tier <= 1 pour les salles normales
            if available_patterns:
                chosen_pattern = rng.choice(available_patterns)
                room.add_pattern(chosen_pattern)
        if room.room_type == "spawn":
            available_patterns = [
                pattern for pattern in room_patterns if pattern.tier == 0
            ]  # Exemple: tier <= 1 pour la salle de spawn
            if available_patterns:
                chosen_pattern = rng.choice(available_patterns)
                room.add_pattern(chosen_pattern)
        if room.room_type == "boss":
            available_patterns = [
                pattern for pattern in room_patterns if pattern.tier == 2
            ]  # Exemple: tier >= 2 pour la salle de boss
            if available_patterns:
                chosen_pattern = rng.choice(available_patterns)
                room.add_pattern(chosen_pattern)


def generate_paths(
    grid: list[tuple[int, int]],
    rooms: list[Room],
    seed: int,
    max_rooms: int = 10,
    continuity_bias: float = 0.5,
    previous_dir=None,
    visited: set[tuple[int, int]] | None = None,
) -> list[Room]:
    """Génère des chemins entre les salles."""
    path_sub_seed = derive_seed(seed, "paths")
    rng = random.Random(path_sub_seed)
    if visited is None:
        visited = set()

    # Vérifies l'existence d'une salle de spawn
    spawn_room = next((room for room in rooms if room.room_type == "spawn"), None)
    if spawn_room is None:
        raise ValueError("Aucune salle de spawn trouvée.")
    visited.add(spawn_room.coord)  # Marquer la salle de spawn comme visitée

    new_rooms = []

    spawn_neighbors = {
        "north": (spawn_room.coord[0], spawn_room.coord[1] - 1),
        "south": (spawn_room.coord[0], spawn_room.coord[1] + 1),
        "west": (spawn_room.coord[0] - 1, spawn_room.coord[1]),
        "east": (spawn_room.coord[0] + 1, spawn_room.coord[1]),
    }

    # Vérifier quels voisins sont disponibles pour la génération de chemins
    available_directions = {
        direction: coord
        for direction, coord in spawn_neighbors.items()
        if coord in grid and coord not in visited
    }
    if not available_directions:
        return new_rooms  # Aucun voisin disponible pour générer des chemins

    # Répartir le budget de salles entre les directions disponibles
    direction_budgets = split_budget(list(available_directions.keys()), max_rooms, rng)

    # Placer chaque voisin disponible du spawn
    for direction, coord in available_directions.items():
        if direction_budgets[direction] > 0:
            new_room = Room(coord=coord, room_type="room")
            new_rooms.append(new_room)
            visited.add(coord)  # Marquer la nouvelle salle comme visitée

            # Générer des chemins à partir de la nouvelle salle
            path_length = (
                direction_budgets[direction] - 1
            )  # Déduire la salle déjà placée
            if path_length > 0:
                path = find_available_neighbors(
                    coord,
                    rng,
                    grid,
                    visited,
                    step=path_length,
                    previous_dir=previous_dir,
                    continuity_bias=continuity_bias,
                )
                if path:
                    for p in path:
                        new_rooms.append(Room(coord=p, room_type="room"))
                        visited.add(p)  # Marquer chaque salle du chemin comme visitée
    return new_rooms


def build_grid(w, h) -> list[tuple[int, int]]:
    return [(x, y) for x in range(w) for y in range(h)]


def generate_dungeon(
    seed: int,
    continuity_bias: float = 0.6,
    w: int = 10,
    h: int = 10,
    max_rooms: int = 20,
) -> tuple[list[tuple[int, int]], list[Room], dict[str, int]]:
    loot_tables = _loading_loot_tables()  # Chargement des tables de loot
    if not loot_tables:
        return [], [], {"status": 3, "message": "Failed to load loot tables."}

    ennemy_tables = _loading_ennemy_tables()  # Chargement des tables d'ennemis
    if not ennemy_tables:
        return [], [], {"status": 3, "message": "Failed to load enemy tables."}

    room_patterns = _loading_room_patterns()  # Chargement des motifs de salle
    if not room_patterns:
        return [], [], {"status": 3, "message": "Failed to load room patterns."}
    status_dict = {"status": 0, "message": "Dungeon generated successfully."}
    if (
        max_rooms >= (w * h) - 2
    ):  # On retire 2 pour la salle de spawn et la salle de boss pour le moment
        status_dict = {
            "status": 1,
            "message": f"max_rooms ({max_rooms}) is too high for the grid size ({w}x{h}).",
        }
        return [], [], status_dict

    visited = set()
    grid = build_grid(w, h)
    spawn = place_spawn_room(grid, seed)
    rooms = [spawn] + generate_paths(
        grid,
        [spawn],
        seed,
        max_rooms=max_rooms,
        continuity_bias=continuity_bias,
        previous_dir=spawn.coord,
        visited=visited,
    )
    boss = place_boss_room(spawn, rooms, grid, seed=seed, visited=visited)
    if boss:
        rooms.append(boss)
    else:
        status_dict = {"status": 2, "message": "Failed to place boss room."}
    apply_room_patterns(rooms, room_patterns, seed)
    print(
        f"Generated dungeon with seed {seed}: {len(rooms)} rooms (spawn + boss included)."
    )
    print(
        f"Rooms: {[room.coord for room in rooms]}, Patterns: {[room.pattern.pattern_id if room.pattern else None for room in rooms]}"
    )
    return grid, rooms, status_dict


def print_grid(grid: list[tuple[int, int]], rooms: list[Room] | None = None) -> None:
    if rooms is None:
        rooms = []
    """Affiche la grille avec les salles."""
    grid_dict = {coord: " " for coord in grid}
    for room in rooms:
        grid_dict[room.coord] = room.room_type[0].upper()

    grid_max_width = max(x for x, y in grid) + 1
    grid_max_height = max(y for x, y in grid) + 1

    print("Grille:")
    for y in range(grid_max_height):
        row = ""
        for x in range(grid_max_width):
            row += f"[{x},{y}: {grid_dict[(x, y)]}]"
        print(row)


def seed_to_number(seed_input: str) -> int:
    """Convertit une seed en un nombre entier."""
    digest = hashlib.sha256(seed_input.encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


if __name__ == "__main__":
    grid = build_grid(10, 10)
    rooms = []
    seed_input = input(
        "Entrez une seed (ou appuyez sur Entrée pour une seed aléatoire): "
    )
    if not seed_input:
        seed_input = str(int(time.time()))

    seed = seed_to_number(seed_input.strip())
    print(f"Seed fournie: {seed_input} (numérique: {seed})")
    spawn_room = place_spawn_room(grid, seed)
    rooms.append(spawn_room)
    new_rooms = generate_paths(grid, rooms, seed, max_rooms=15, continuity_bias=0.6)
    rooms.extend(
        new_rooms
    )  # Ajoute les nouvelles salles générées à la liste des salles
    boss_room = place_boss_room(
        spawn_room, rooms, grid, {room.coord for room in rooms}, seed
    )
    if boss_room:
        rooms.append(boss_room)
    print_grid(grid, rooms)
