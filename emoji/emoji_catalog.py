from collections import Counter, defaultdict, namedtuple
import re
from typing import Sequence, Union

from emoji.config import EMOJI_CONFIG

Emoji = namedtuple(
    "Emoji",
    ["literal", "name", "code_points", "status", "group", "subgroup", "version"],
)

EMOJI_LINE = re.compile(
    r"^(?P<code_points>([0-9A-Fa-f]+ )+) *; (?P<status>\S+) +# (?P<emoji>\S+) E(?P<version>\d+\.\d+) (?P<name>.*)$",
)

GROUP_LINE = re.compile(
    r"^# group: (?P<group_name>.+)$",
)

GROUP_COUNT_LINE = re.compile(
    r"^# (?P<group_name>.+) subtotal:\s+(?P<group_count>\d+)$",
)

STATUS_COUNT_LINE = re.compile(
    r"^# (?P<status_name>(fully-qualified|minimally-qualified|unqualified|component)) : (?P<status_count>\d+)$",
)

SUBGROUP_LINE = re.compile(
    r"^# subgroup: (?P<subgroup_name>.+)$",
)


def parse_unicode_test_file(
    lines: list[str],
) -> tuple[dict[str, Emoji], dict[str, int], dict[str, int], dict[str, list[str]]]:
    emoji: dict[str, Emoji] = {}
    group_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}
    group = ""
    subgroup = ""
    names: dict[str, str] = {}
    variants: dict[str, list[str]] = defaultdict(list)
    for line in [line.strip() for line in lines if line.strip() != ""]:
        if line[0] == "#":
            if match := GROUP_LINE.match(line):
                group = match.group("group_name")
            elif match := GROUP_COUNT_LINE.match(line):
                assert group == match.group("group_name")
                group_counts[group] = int(match.group("group_count"))
            elif match := STATUS_COUNT_LINE.match(line):
                status_counts[match.group("status_name")] = int(
                    match.group("status_count")
                )
            elif match := SUBGROUP_LINE.match(line):
                subgroup = match.group("subgroup_name")
        elif match := EMOJI_LINE.match(line):
            literal = match.group("emoji")
            name = match.group("name")
            names[name] = literal
            if len(parts := name.split(":")) > 1:
                base, _ = parts
                if base in names:
                    variants[names[base]].append(literal)
            emoji[literal] = Emoji(
                code_points=match.group("code_points").strip().split(),
                group=group,
                literal=literal,
                name=name,
                status=match.group("status"),
                subgroup=subgroup,
                version=match.group("version"),
            )
    return (emoji, group_counts, status_counts, variants)


UNICODE_TEST_FILE_PATH = EMOJI_CONFIG["unicode_test_file"]

with open(UNICODE_TEST_FILE_PATH, "r") as unicode_emoji_test_file:
    PARSED_EMOJI_METADATA = parse_unicode_test_file(unicode_emoji_test_file.readlines())

EMOJI_CATALOG, _, _, EMOJI_VARIANTS = PARSED_EMOJI_METADATA
