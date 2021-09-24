import json

from emoji.config import EMOJI_CONFIG
from emoji.emoji_catalog import EMOJI_BY_NAME, EMOJI_CATALOG, EMOJI_VARIANTS
from emoji.image_catalog import ALL_RESOLVED_EMOJI


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


SKIN_TONES = {
    "1F3FB": "skin-tone-light",
    "1F3FC": "skin-tone-medium-light",
    "1F3FD": "skin-tone-medium",
    "1F3FE": "skin-tone-medium-dark",
    "1F3FF": "skin-tone-dark",
}


def derive_skin_tone_aliases(literal: str, base_alias: str) -> dict[str, str]:
    aliases: dict[str, str] = {}
    if literal in EMOJI_VARIANTS:
        for variant in EMOJI_VARIANTS[literal]:
            skin_tones = ":".join(
                [
                    SKIN_TONES[p]
                    for p in EMOJI_CATALOG[variant].code_points
                    if p in SKIN_TONES
                ]
            )
            aliases[f"{base_alias}:{skin_tones}"] = variant
    return aliases


def load_emoji_aliases():
    aliases_to_emoji = dict()
    # Load the gemoji aliases.
    with open(EMOJI_CONFIG["gemoji_alias_file"], "r") as gemoji_alias_file:
        gemoji_aliases = json.load(gemoji_alias_file)
    for entry in gemoji_aliases:
        literal = entry.get("emoji")
        if literal not in ALL_RESOLVED_EMOJI:
            # try other literals with the same name
            for other in EMOJI_BY_NAME[EMOJI_CATALOG[literal].name]:
                if other in ALL_RESOLVED_EMOJI:
                    literal = other
        if literal in ALL_RESOLVED_EMOJI:
            for alias in entry["aliases"]:
                aliases_to_emoji[alias] = literal
                if entry.get("skin_tones", False):
                    aliases_to_emoji.update(derive_skin_tone_aliases(literal, alias))

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
    for emoji_set_name in reversed(EMOJI_CONFIG["priority"]):
        set_config = EMOJI_CONFIG["set_config"][emoji_set_name]
        if "alias_map" in set_config:
            with open(set_config["alias_map"], "r") as set_alias_map_file:
                set_alias_map = json.load(set_alias_map_file)
            for emoji, aliases in set_alias_map.items():
                for alias in aliases:
                    aliases_to_emoji[alias] = emoji
    return aliases_to_emoji


ALIASES_TO_EMOJI = load_emoji_aliases()
