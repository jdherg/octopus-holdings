import json
import pathlib

with open(pathlib.Path(__file__).with_name("emoji_config.json")) as f:
    EMOJI_CONFIG = json.load(f)
