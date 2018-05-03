import json
import os
import random
import re

with open("emoji_config.json", 'r') as emoji_config_file:
    EMOJI_CONFIG = json.load(emoji_config_file)

def load_emoji_config():
    emoji_set_paths = dict()
    for config in EMOJI_CONFIG["set_config"].values():
        emoji_set_paths[config["external_path"]] = config["internal_path"]
    return EMOJI_CONFIG["priority"], EMOJI_CONFIG["set_config"], emoji_set_paths

def generate_emoji_aliases(set_config):
    svg_folder = set_config["internal_path"]
    svg_filename_regex = re.compile(set_config["svg_filename_regex"])
    with open(EMOJI_CONFIG["gemoji_alias_file"], 'r') as gemoji_alias_file:
        gemoji_aliases = json.load(gemoji_alias_file)
    gemoji_aliases = {entry["emoji"]: entry
                      for entry in gemoji_aliases
                      if "emoji" in entry}
    svg_filenames = os.listdir(svg_folder)
    emoji_to_alias_mappings = {}
    supported_emoji = set()
    for svg_filename in svg_filenames:
        if svg_filename_regex.search(svg_filename):
            aliases = []
            svg_codepoint = svg_filename_regex.search(svg_filename).group()
            emoji = "".join([chr(int(char, 16)) for char in re.split(r'[\-_]', svg_codepoint)])
            supported_emoji.add(emoji)
            aliases.append(emoji)
            aliases.append(svg_codepoint)
            aliases.append("u" + svg_codepoint)
            if emoji in gemoji_aliases:
                aliases.extend(gemoji_aliases[emoji]["aliases"])
                # Noto filenames don't include the variation selector-16 (\ufe0f)
                # but gemoji does. The first miss may be because of that.
            elif emoji + "\ufe0f" in gemoji_aliases:
                aliases.extend(gemoji_aliases[emoji + "\ufe0f"]["aliases"])
            emoji_to_alias_mappings[svg_codepoint] = aliases
    return emoji_to_alias_mappings, supported_emoji

def load_emoji_aliases(set_config):
    if "alias_map" in set_config:
        with open(set_config["alias_map"], 'r') as alias_file:
            emoji_dict = json.load(alias_file)
        set_emoji = set(emoji_dict.keys())
    else:
        emoji_dict, set_emoji = generate_emoji_aliases(set_config)
    set_aliases = dict()
    for emoji in emoji_dict.keys():
        emoji_path = set_config["prefix"] + emoji + ".svg"
        if set_config["external_path"]:
            emoji_path = set_config["external_path"] + "/" + emoji_path
        for alias in emoji_dict[emoji]:
            set_aliases[alias] = emoji_path
    return set_aliases, set_emoji

EMOJI_SET_PRIORITY, EMOJI_SET_CONFIG, EMOJI_SET_PATHS = load_emoji_config()

def load_all_emoji_aliases():
    emoji_aliases = dict()
    all_emoji = set()
    for emoji_set_name in EMOJI_SET_PRIORITY:
        emoji_aliases[emoji_set_name], set_emoji = load_emoji_aliases(
            EMOJI_SET_CONFIG[emoji_set_name])
        all_emoji |= set_emoji
    return emoji_aliases, list(all_emoji)

EMOJI_ALIASES, ALL_EMOJI = load_all_emoji_aliases()

def is_emoji_set(candidate):
    return candidate in EMOJI_ALIASES.keys()

def resolve(alias, desired_set=None):
    if desired_set and is_emoji_set(desired_set):
        return EMOJI_ALIASES[desired_set].get(alias) or resolve(alias)
    for set_name in EMOJI_SET_PRIORITY:
        if alias in EMOJI_ALIASES[set_name]:
            return EMOJI_ALIASES[set_name].get(alias)
    return resolve("question")

def resolve_to_internal_path(external_path):
    if external_path.find('/') == -1:
        path, base = ("", external_path)
    else:
        path, base = external_path.rsplit('/', 1)
    if path in EMOJI_SET_PATHS:
        return (EMOJI_SET_PATHS[path], base)
    return None

def random_emoji():
    return random.choice(ALL_EMOJI)
