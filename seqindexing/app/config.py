import yaml
from pathlib import Path

# Load YAML config
CONFIG_PATH = Path(__file__).parent / "config.yaml"

with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

# Access fonts
FONT_FAMILY = config["fonts"]["family"]
TITLE_FONT_SIZE = config["fonts"]["title_size"]
LABEL_FONT_SIZE = config["fonts"]["label_size"]
SMALL_FONT_SIZE = config["fonts"]["small_size"]

# Colors
PRIMARY_COLOR = config["colors"]["primary"]
BACKGROUND_COLOR = config["colors"]["background"]
BORDER_COLOR = config["colors"]["border"]
SELECTED_BORDER = f"3px solid {PRIMARY_COLOR}"
UNSELECTED_BORDER = f"1px solid {BORDER_COLOR}"

# Layout
PREVIEW_HEIGHT = config["layout"]["preview_height"]
PREVIEW_CARD_HEIGHT = config["layout"]["preview_card_height"]
PREVIEW_FONT_SIZE = SMALL_FONT_SIZE

# data
SERIES_WINDOW_SIZE = config["series"]["window_size"]