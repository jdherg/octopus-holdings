import json
import os
import random
import re

from emoji.config import EMOJI_CONFIG
from emoji.alias_catalog import ALIASES_TO_EMOJI, ALL_RESOLVED_EMOJI
from emoji.image_catalog import EMOJI_TO_SVGS


def load_emoji_set_config():
    emoji_set_paths = dict()
    for config in EMOJI_CONFIG["set_config"].values():
        emoji_set_paths[config["external_path"]] = config["internal_path"]
    return EMOJI_CONFIG["priority"], EMOJI_CONFIG["set_config"], emoji_set_paths


EMOJI_SET_PRIORITY, EMOJI_SET_CONFIG, EMOJI_SET_PATHS = load_emoji_set_config()


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
