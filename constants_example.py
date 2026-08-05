# Constants for the dungeon generator and visualization
CELL_SIZE : int = 40  # Size of each cell in pixels
GRID_W : int = 10  # Width of the grid in cells
GRID_H : int = 10  # Height of the grid in cells
MARGIN : int = 20  # Margin around the grid in pixels
MAX_ROOMS : int = 10  # Maximum number of rooms
CONTINUITY_BIAS : float = 1.0  # Bias for continuity in room placement

# Recommended to not change these colors unless you want to customize the appearance
COLOR_BG = (24, 24, 28)
COLOR_GRID_LINE = (55, 55, 62)
COLOR_EMPTY = (40, 40, 46)
COLOR_ROOM = (70, 130, 220)
COLOR_SPAWN = (70, 200, 120)
COLOR_BOSS = (220, 70, 70)
COLOR_TEXT = (230, 230, 230)
