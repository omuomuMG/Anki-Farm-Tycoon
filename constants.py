from pathlib import Path

ADDON_DIR = Path(__file__).parent
RESOURCES_DIR = ADDON_DIR / "Resources"

# Game settings
INITIAL_MONEY = 1500
CELL_SIZE = 100
STATS_PANEL_WIDTH = 250
GRID_SIZE = 4
MAX_GROWTH = 150
GROWTH_RATE = 3

# Production chances
CHICKEN_PRODUCTION_CHANCE = 0.10
COW_PRODUCTION_CHANCE = 0.02
PIG_PRODUCTION_CHANCE = 0.01

# Production values
CHICKEN_MIN_PRODUCTION = 5
CHICKEN_MAX_PRODUCTION = 10
COW_PRODUCTION_VALUE = 50

# Field prices
BASE_FIELD_PRICE = 500
FIELD_PRICE_MULTIPLIER = 1.5

VERSION = "1.2.1"