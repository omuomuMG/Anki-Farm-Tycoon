from pathlib import Path

ADDON_DIR = Path(__file__).parent
RESOURCES_DIR = ADDON_DIR / "Resources"

# Game settings
INITIAL_MONEY = 1500
INITIAL_CELL_SIZE = 100
STATS_PANEL_WIDTH = 250
GRID_SIZE = 4
MAX_GROWTH = 150
GROWTH_RATE = 3

# Growth ranges by animal (min, max) per reviewed card
CHICKEN_GROWTH_RANGE = (1, 4)
PIG_GROWTH_RANGE = (0, 3)
COW_GROWTH_RANGE = (0, 2)
HORSE_GROWTH_RANGE = (0, 1)

# Production chances
CHICKEN_PRODUCTION_CHANCE = 0.10
COW_PRODUCTION_CHANCE = 0.02
PIG_PRODUCTION_CHANCE = 0.01

# Production values
CHICKEN_MIN_PRODUCTION = 5
CHICKEN_MAX_PRODUCTION = 10
COW_PRODUCTION_VALUE = 50

# Pig sale bonus from breed level
PIG_SALE_BONUS_PER_LEVEL = 0.015

# Field prices
BASE_FIELD_PRICE = 500
FIELD_PRICE_MULTIPLIER = 1.5

VERSION = "1.6.0"

# --- Sheep ---
SHEEP_GROWTH_RANGE = (0, 2)
SHEEP_PRODUCTION_CHANCE = 0.05
SHEEP_BASE_PRICE = 500
SHEEP_AGAIN_BONUS_PER_CARD = 0.05   # +5% sale price per "Again" answered this cycle

# --- Chicken+Cow synergy ---
CHICKEN_COW_SYNERGY_MULTIPLIER = 2   # egg value doubles when a cow is present

# --- Random events ---
RANDOM_EVENT_CHANCE = 0.02           # 2% per card
RANDOM_EVENT_FAIR_MULTIPLIER = 2     # next sale worth 2x
RANDOM_EVENT_RAIN_BOOST = 5          # all animals +5% growth
RANDOM_EVENT_EPIDEMIC_LOSS = 10      # one random animal loses 10% growth
RANDOM_EVENT_HARVEST_BONUS = 50      # instant +50 coins

# --- Unicorn (legendary) ---
UNICORN_EASY_STREAK_REQUIRED = 5     # consecutive "Easy" cards to summon
UNICORN_GROWTH_RANGE = (0, 1)
UNICORN_BASE_PRICE = 3000
UNICORN_COOLDOWN_CARDS = 50          # cards to wait after unicorn dies

# Animal render tuning (per animal x stage)
# scale: Multiplier for base size
# offset_x / offset_y: Pixel offset from centered position
ANIMAL_RENDER_SETTINGS = {
    "PIG": {
        "adult": {"scale": 1.0, "offset_x": 0, "offset_y": 0},
        "child": {"scale": 0.8, "offset_x": 0, "offset_y": 10},
    },
    "CHICKEN": {
        "adult": {"scale": 0.9, "offset_x": 0, "offset_y": 0},
        "child": {"scale": 0.7, "offset_x": 0, "offset_y": 10},
    },
    "COW": {
        "adult": {"scale": 1.0, "offset_x": 0, "offset_y": 0},
        "child": {"scale": 0.8, "offset_x": 0, "offset_y": 10},
    },
    "HORSE": {
        "adult": {"scale": 1.0, "offset_x": 0, "offset_y": 0},
        "child": {"scale": 0.9, "offset_x": 0, "offset_y": 10},
    },
    "SHEEP": {
        "adult": {"scale": 1.0, "offset_x": 0, "offset_y": 0},
        "child": {"scale": 0.8, "offset_x": 0, "offset_y": 10},
    },
    "UNICORN": {
        "adult": {"scale": 1.0, "offset_x": 0, "offset_y": 0},
        "child": {"scale": 0.9, "offset_x": 0, "offset_y": 10},
    },
}
