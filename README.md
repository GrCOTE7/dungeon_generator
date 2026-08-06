# Dungeon Generator

Générateur procédural de donjons en grille, basé sur un seed reproductible, avec un viewer Pygame minimaliste pour visualiser le résultat.

## Principe

À partir d'une grille 2D et d'un seed, le générateur :

1. **Place la salle de spawn** (`place_spawn_room`): favorise un placement central.
2. **Génère des chemins de salles** (`generate_paths`): depuis le spawn, répartis dans les 4 directions (nord/sud/est/ouest), chaque direction recevant un budget de salles réparti aléatoirement.
3. **Fait avancer chaque chemin récursivement**: (`find_available_neighbors`) case par case, avec un biais de continuité (`continuity_bias`) qui favorise le prolongement en ligne droite plutôt qu'un zigzag aléatoire.
4. **Place la salle du boss** (`place_boss_room`): cherche une case adjacente à une seule salle occupée la plus éloignée possible du spawn.

Chacun de ces sous-système dérive la seed avec un sel dessus.

## Fichiers

- `dungeon_gen.py`: logique de génération : grille, salles, pathfinding récursif, placement spawn/boss.
- `main.py`: viewer Pygame minimaliste pour visualiser un donjon généré.

## Installer les deps (si nécessaire) et lancer le viewer

### Prérequis : [**uv** ↗](https://docs.astral.sh/uv/getting-started/installation) doit être installé.

### Mode Desktop App

```bash
./go
```

(Sous linux (ou wsl), le hot-reload perd le focus de l'éditeur - ALT + TAB permet de l'y récupérer)

### Mode Web App

```bash
./go w
```

### Sans aucune installation, dans un CodeSpace

[Doc pour usage CodeSpace](./doc/CODESPACES.md)

### Contrôles

| Touche   | Action                                      |
|----------|----------------------------------------------|
| `R`      | Régénère avec un nouveau seed aléatoire       |
| `ESPACE` | Régénère avec le seed suivant (seed + 1)      |
| `ECHAP`  | Quitte                                        |

### Légende des couleurs

| Couleur | Type de salle |
|---------|----------------|
| 🔴 Rouge | Spawn |
| 🟢 Vert  | Boss |
| 🔵 Bleu  | Salle normale |
| ⬛ Gris  | Case vide / inutilisée |

En cas d'exception pendant la génération (budget impossible à atteindre, etc.), le viewer affiche un écran d'erreur avec le message et le seed concerné, plutôt que de crasher : pratique pour reproduire et débugger une seed problématique.

## Paramètres clés

- `max_rooms`: Nombre de salle voulue en plus du spawn et du boss.
- `continuity_bias` (0 à 1): 1 chemin plus rectiligne, 0 chemin qui serpente.
## Limitations connues

- Formation de "blob" de salle récurrents malgré le continuity_bias à 1, un virage tôt fait se rejoindre les chemins.