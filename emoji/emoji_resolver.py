import json
import os
import random
import re

from emoji.config import EMOJI_CONFIG
from emoji.image_catalog import load_emoji_set_svgs


def load_emoji_set_config():
    emoji_set_paths = dict()
    for config in EMOJI_CONFIG["set_config"].values():
        emoji_set_paths[config["external_path"]] = config["internal_path"]
    return EMOJI_CONFIG["priority"], EMOJI_CONFIG["set_config"], emoji_set_paths


EMOJI_SET_PRIORITY, EMOJI_SET_CONFIG, EMOJI_SET_PATHS = load_emoji_set_config()


def load_all_emoji_svgs():
    all_resolved_emoji = set()
    emoji_to_svgs = dict()
    for emoji_set_name in EMOJI_SET_PRIORITY:
        emoji_to_svgs[emoji_set_name], set_emoji = load_emoji_set_svgs(
            EMOJI_SET_CONFIG[emoji_set_name]
        )
        all_resolved_emoji |= set_emoji
    return all_resolved_emoji, emoji_to_svgs


ALL_RESOLVED_EMOJI, EMOJI_TO_SVGS = load_all_emoji_svgs()


def derive_codepoint_aliases(emoji):
    aliases = set()
    # Reflection.
    aliases.add(emoji)
    hex_codepoints = [hex(ord(c))[2:].lower() for c in emoji]
    # The Noto filename substrings for backwards-compatibility.
    noto_codepoints = [codepoint.rjust(4, "0") for codepoint in hex_codepoints]
    aliases.add("_".join(noto_codepoints))
    aliases.add("u" + "_".join(noto_codepoints))
    # The Twemoji filename substrings for backwards-compatibility.
    aliases.add("-".join(hex_codepoints))
    return aliases


def load_emoji_aliases():
    aliases_to_emoji = dict()
    # Load the gemoji aliases.
    with open(EMOJI_CONFIG["gemoji_alias_file"], "r") as gemoji_alias_file:
        gemoji_aliases = json.load(gemoji_alias_file)
    for entry in gemoji_aliases:
        if "emoji" in entry and entry["emoji"] in ALL_RESOLVED_EMOJI:
            for alias in entry["aliases"]:
                aliases_to_emoji[alias] = entry["emoji"]
    # Add aliases derived from codepoints.
    variation_selector_16 = "\ufe0f"
    for emoji in ALL_RESOLVED_EMOJI:
        codepoint_aliases = set()
        codepoint_aliases.add(emoji)
        codepoint_aliases |= derive_codepoint_aliases(emoji)
        # U+FE0F VARIATION SELECTOR-16 is optional.
        if emoji[-1] == variation_selector_16:
            variant = emoji[:-1]
        else:
            variant = emoji + variation_selector_16
        if variant not in ALL_RESOLVED_EMOJI:
            codepoint_aliases |= derive_codepoint_aliases(variant)
        for alias in codepoint_aliases:
            aliases_to_emoji[alias] = emoji
    # Load custom emoji aliases.
    # This goes last (and is ordered from lowest to highest priority) so that
    # so they can overwrite standard aliases in the case of a conflict.
    for emoji_set_name in reversed(EMOJI_SET_PRIORITY):
        set_config = EMOJI_SET_CONFIG[emoji_set_name]
        if "alias_map" in set_config:
            with open(set_config["alias_map"], "r") as set_alias_map_file:
                set_alias_map = json.load(set_alias_map_file)
            for emoji, aliases in set_alias_map.items():
                for alias in aliases:
                    aliases_to_emoji[alias] = emoji
    return aliases_to_emoji


ALIASES_TO_EMOJI = load_emoji_aliases()


def is_emoji_set(candidate):
    return candidate in EMOJI_SET_PRIORITY


def resolve_alias(alias):
    return ALIASES_TO_EMOJI.get(alias, None)


def resolve_emoji(emoji, desired_set):
    if desired_set and is_emoji_set(desired_set):
        return EMOJI_TO_SVGS[desired_set].get(emoji) or resolve_emoji(emoji, None)
    for set_name in EMOJI_SET_PRIORITY:
        if emoji in EMOJI_TO_SVGS[set_name]:
            return EMOJI_TO_SVGS[set_name].get(emoji)
    return None


def resolve(alias, desired_set=None):
    emoji = resolve_alias(alias)
    if emoji:
        return resolve_emoji(emoji, desired_set)
    return resolve_emoji(resolve_alias("question"), desired_set)


def resolve_to_internal_path(external_path):
    if external_path.find("/") == -1:
        path, base = ("", external_path)
    else:
        path, base = external_path.rsplit("/", 1)
    if path in EMOJI_SET_PATHS:
        return (EMOJI_SET_PATHS[path], base)
    return None


def random_emoji():
    return random.sample(ALL_RESOLVED_EMOJI, 1)[0]
