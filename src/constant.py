# Position of the App window
APP_LEFT = 910
APP_TOP  =   0
# Example pour un écran de 1920 x 1080 :
# - Linux   : 1460, 30
# - Windows : 1478, 30
# - Vidéos  :  910,  0

# Constants for the dungeon generator and visualization
CELL_SIZE : int = 40  # Size of each cell in pixels
GRID_W : int = 10  # Width of the grid in cells
GRID_H : int = 10  # Height of the grid in cells
MARGIN : int = 20  # Margin around the grid in pixels
MAX_ROOMS : int = 10  # Maximum number of rooms
CONTINUITY_BIAS : float = 1.0  # Bias for continuity in room placement, min: 0.0 max: 1.0

# Recommended to not change these colors unless you want to customize the appearance
COLOR_BG = (24, 24, 28)
COLOR_GRID_LINE = (55, 55, 62)
COLOR_EMPTY = (40, 40, 46)
COLOR_ROOM = (70, 130, 220)
COLOR_SPAWN = (70, 200, 120)
COLOR_BOSS = (220, 70, 70)
COLOR_TEXT = (230, 230, 230)
