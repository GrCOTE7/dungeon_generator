import random
import hashlib
import time
grid_max_width = 10
class Room:
    room_type: str = "room" # Type de la salle (par défaut "room")
    coord: tuple[int, int] # Coordonnées de la salle (x, y)

    def __init__(self, coord: tuple[int, int], room_type: str = "room") -> None:
        self.coord = coord
        self.room_type = room_type

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
    spawn_coord = rng.choices(grid, k=1)[0]
    return Room(coord=spawn_coord, room_type="spawn")

def split_budget(directions: dict[str, dict], total_budget: int, rng: random.Random) -> dict[str, int]:
    """Répartit un budget total entre les directions disponibles"""
    direction_keys = list(directions.keys())

    raw_weights = {d: rng.uniform(0.7, 1.3) for d in direction_keys}
    total_weight = sum(raw_weights.values())

    budgets = {d: round(total_budget * w / total_weight) for d, w in raw_weights.items()}

    diff = total_budget - sum(budgets.values())
    if diff != 0:
        adjust_direction = rng.choice(direction_keys)
        budgets[adjust_direction] += diff

    return budgets

def generate_paths(grid: list[tuple[int, int]], rooms: list[Room], seed: int, max_rooms: int = 10) -> list[Room]:
    """Génère des chemins entre les salles."""
    path_sub_seed = derive_seed(seed, "paths")
    rng = random.Random(path_sub_seed)
    path_weight_by_direction = {}
    visited = set()

    # Vérifies l'existence d'une salle de spawn
    spawn_room = next((room for room in rooms if room.room_type == "spawn"), None)
    if spawn_room is None:
        raise ValueError("Aucune salle de spawn trouvée.")
    visited.add(spawn_room.coord)

    # Vérife quel voisin est disponible pour créer un chemin
    north = (spawn_room.coord[0], spawn_room.coord[1] - 1)
    south = (spawn_room.coord[0], spawn_room.coord[1] + 1)
    west = (spawn_room.coord[0] - 1, spawn_room.coord[1])
    east = (spawn_room.coord[0] + 1, spawn_room.coord[1])

    print(f"Voisins disponibles pour la salle de spawn à {spawn_room.coord}:")
    if north in grid:
        print(f"  North: {north}")
    if south in grid:
        print(f"  South: {south}")
    if west in grid:
        print(f"  West: {west}")
    if east in grid:
        print(f"  East: {east}")

    # Lister les directions disponibles et initialiser les poids des chemins
    if north in grid:
        path_weight_by_direction["north"] = {"budget": 0, "max_allowable_distance": 0}
    if south in grid:
        path_weight_by_direction["south"] = {"budget": 0, "max_allowable_distance": 0}
    if west in grid:
        path_weight_by_direction["west"] = {"budget": 0, "max_allowable_distance": 0}
    if east in grid:
        path_weight_by_direction["east"] = {"budget": 0, "max_allowable_distance": 0}
    
    # trouver les distances maximales autorisées pour chaque direction en fonction de la position de la salle de spawn
    north_distance_with_edge = spawn_room.coord[1]  
    south_distance_with_edge = grid_max_width - 1 - spawn_room.coord[1]
    west_distance_with_edge = spawn_room.coord[0]  
    east_distance_with_edge = grid_max_width - 1 - spawn_room.coord[0]
    
    if "north" in path_weight_by_direction:
        path_weight_by_direction["north"]["max_allowable_distance"] = north_distance_with_edge
    if "south" in path_weight_by_direction:
        path_weight_by_direction["south"]["max_allowable_distance"] = south_distance_with_edge
    if "west" in path_weight_by_direction:
        path_weight_by_direction["west"]["max_allowable_distance"] = west_distance_with_edge
    if "east" in path_weight_by_direction:
        path_weight_by_direction["east"]["max_allowable_distance"] = east_distance_with_edge

    print(f"Distances maximales autorisées par direction: {path_weight_by_direction}")

    budgets = split_budget(path_weight_by_direction, total_budget=max_rooms, rng=rng)
    print(f"Budgets répartis par direction: {budgets}")

    for direction in path_weight_by_direction:
        path_weight_by_direction[direction]["budget"] = budgets[direction]

    new_rooms = []
    initial_room_list = {}
    # on place les salles initiale de chaque direction
    for direction, info in path_weight_by_direction.items():
        budget = info["budget"]
        max_distance = info["max_allowable_distance"]
        if budget > 0 and max_distance > 0:
            if direction == "north":
                new_coord = (spawn_room.coord[0], spawn_room.coord[1] - 1)
            elif direction == "south":
                new_coord = (spawn_room.coord[0], spawn_room.coord[1] + 1)
            elif direction == "west":
                new_coord = (spawn_room.coord[0] - 1, spawn_room.coord[1])
            elif direction == "east":
                new_coord = (spawn_room.coord[0] + 1, spawn_room.coord[1])
            else:
                continue

            if new_coord in grid and new_coord not in visited:
                new_room = Room(coord=new_coord, room_type="room")
                rooms.append(new_room)
                new_rooms.append(new_room)
                initial_room_list[direction] = new_room
                visited.add(new_coord)
                print(f"Salle ajoutée à {new_coord} dans la direction {direction}.")
            else:
                print(f"Impossible d'ajouter une salle à {new_coord} dans la direction {direction} (hors grille ou déjà visitée).")


    # Maintenant on récupère chaque salle initiale et on génère des chemins supplémentaires à partir de celle-ci
    for room in initial_room_list:
        current_room = initial_room_list[room]
        direction = room
        budget = path_weight_by_direction[direction]["budget"]
        max_distance = path_weight_by_direction[direction]["max_allowable_distance"]

        for _ in range(budget - 1):  # On a déjà placé une salle, donc on fait budget - 1
            neighbor_coord = { "north": (current_room.coord[0], current_room.coord[1] - 1),
                               "south": (current_room.coord[0], current_room.coord[1] + 1),
                               "west": (current_room.coord[0] - 1, current_room.coord[1]),
                               "east": (current_room.coord[0] + 1, current_room.coord[1]) }
            print(f"Tentative de placement d'une nouvelle salle à partir de {current_room.coord} dans la direction {direction}. Voisinage: {neighbor_coord}")
            valide_direction = False
            retry_count = 0
            while not valide_direction and retry_count < 5:
                retry_count += 1
                new_coord = rng.choice(list(neighbor_coord.values()))
                if new_coord in grid and new_coord not in visited:
                    valide_direction = True
                else:
                    print(f"Coordonnée {new_coord} invalide pour la direction {direction}, tentative de nouvelle coordonnée.")

            if new_coord in grid and new_coord not in visited:
                new_room = Room(coord=new_coord, room_type="room")
                rooms.append(new_room)
                new_rooms.append(new_room)
                visited.add(new_coord)
                current_room = new_room  # Met à jour la salle actuelle pour la prochaine itération
                print(f"Salle ajoutée à {new_coord} dans la direction {direction}.")
            else:
                print(f"Impossible d'ajouter une salle à {new_coord} dans la direction {direction} (hors grille ou déjà visitée).")
                break  # Arrête de générer des salles dans cette direction si on ne peut pas en ajouter

    return new_rooms

def print_grid(grid: list[tuple[int, int]], rooms: list[Room] | None = None) -> None:
    if rooms is None:
        rooms = []
    """Affiche la grille avec les salles."""
    grid_dict = {coord: " " for coord in grid}
    for room in rooms:
        grid_dict[room.coord] = room.room_type[0].upper()  # Utilise la première lettre du type de salle

    print("Grille:")
    for y in range(grid_max_width):
        row = ""
        for x in range(grid_max_width):
            row += f"[{x},{y}: {grid_dict[(x, y)]}]"
        print(row)

def seed_to_number(seed_input: str) -> int:
    """Convertit une seed en un nombre entier."""
    digest = hashlib.sha256(seed_input.encode("utf-8")).hexdigest()
    return int(digest[:16], 16)



if __name__ == "__main__":
    grid = [(x, y) for x in range(grid_max_width) for y in range(grid_max_width)]
    rooms = []
    seed_input = input("Entrez une seed (ou appuyez sur Entrée pour une seed aléatoire): ")
    if not seed_input:
        for i in range(3):
            seed_input = random.randbytes(16).hex()
            seed = seed_to_number(seed_input.strip())
            spawn_room = place_spawn_room(grid, seed)
            rooms.append(spawn_room)
            generate_paths(grid, rooms, seed)
            print_grid(grid, rooms)
            rooms.clear()  # Réinitialise la liste des salles pour la prochaine itération
    else:
        seed = seed_to_number(seed_input.strip())
        print(f"Seed fournie: {seed_input} (numérique: {seed})")
        spawn_room = place_spawn_room(grid, seed)
        rooms.append(spawn_room)
        new_rooms = generate_paths(grid, rooms, seed, max_rooms=15)
        rooms.extend(new_rooms)  # Ajoute les nouvelles salles générées à la liste des salles
        print_grid(grid, rooms)

