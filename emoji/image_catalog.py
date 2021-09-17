import itertools
import json
import os
import re

from emoji.config import EMOJI_CONFIG
from emoji.emoji_catalog import EMOJI_CATALOG


def load_emoji_set_svgs(set_config):
    emoji_to_svgs = dict()
    set_emoji = set()
    external_prefix = ""
    if set_config["external_path"]:
        external_prefix = set_config["external_path"] + "/"
    svg_folder = set_config["internal_path"]
    svg_filename_regex = re.compile(set_config["svg_filename_regex"])
    svg_folder_filenames = os.listdir(svg_folder)
    for filename in svg_folder_filenames:
        if svg_filename_regex.search(filename):
            svg_codepoint = svg_filename_regex.search(filename).group()
            if "alias_map" in set_config:
                emoji = svg_codepoint
            else:
                emoji = "".join(
                    [chr(int(char, 16)) for char in re.split(r"[\-_]", svg_codepoint)]
                )
            emoji_path = external_prefix + filename
            emoji_to_svgs[emoji] = emoji_path
            set_emoji.add(emoji)
    return emoji_to_svgs, set_emoji


def load():

    set_config = EMOJI_CONFIG["set_config"]

    result: dict[str, dict[str, str]] = {}

    for name, config in set_config.items():
        if config.get("alias_map") is not None:
            continue
        emoji_to_svgs, _ = load_emoji_set_svgs(config)
        result[name] = emoji_to_svgs

    return result


IMAGE_CATALOGS = load()


def main():
    unicode_emoji: set[str] = set(EMOJI_CATALOG.keys())
    svg_emoji: set[str] = set(
        itertools.chain(*[x.keys() for x in IMAGE_CATALOGS.values()])
    )
    svg_files: set[str] = set(
        itertools.chain(
            *[[(k, v) for k, v in c.items()] for c in IMAGE_CATALOGS.values()]
        )
    )
    # svg_emoji = svg_emoji | {e + "\uFE0F" for e in svg_emoji}
    present_emoji = [EMOJI_CATALOG[e] for e in unicode_emoji & svg_emoji]
    missing_emoji = [EMOJI_CATALOG[e] for e in unicode_emoji - svg_emoji]
    missing_svg = [v for k, v in svg_files if k not in EMOJI_CATALOG]

    print(f"present {len(present_emoji)}")
    print(f"missing {len(missing_emoji)}")
    print(f"missing svg {len(missing_svg)}")
    from collections import Counter

    c = Counter(map(lambda e: e.version, missing_emoji))
    print(sorted(c.items(), key=lambda i: float(i[0])))
    c = Counter(map(lambda e: e.status, missing_emoji))
    print(sorted(c.items(), key=lambda i: i[0]))
    print(missing_svg[:10])


if __name__ == "__main__":
    main()
