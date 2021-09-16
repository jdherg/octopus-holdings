from collections import Counter, namedtuple
import json
import re
from typing import Dict, List, Sequence, Union

Emoji = namedtuple(
    "Emoji", ["literal", "name", "code_points", "status", "group", "subgroup"]
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
    lines: List[str],
) -> tuple[Dict[str, Emoji], Dict[str, int], Dict[str, int]]:
    emoji: Dict[str, Emoji] = {}
    group_counts: Dict[str, int] = {}
    status_counts: Dict[str, int] = {}
    group = ""
    subgroup = ""
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
            emoji[match.group("emoji")] = Emoji(
                code_points=match.group("code_points").strip().split(),
                group=group,
                literal=match.group("emoji"),
                name=match.group("name"),
                status=match.group("status"),
                subgroup=subgroup,
            )
    return (emoji, group_counts, status_counts)


with open("emoji_config.json", "r") as emoji_config_file:
    UNICODE_TEST_FILE_PATH = json.load(emoji_config_file)["unicode_test_file"]

with open(UNICODE_TEST_FILE_PATH, "r") as unicode_emoji_test_file:
    PARSED_EMOJI_METADATA = parse_unicode_test_file(unicode_emoji_test_file.readlines())

EMOJI_CATALOG = PARSED_EMOJI_METADATA[0]


def check_counts(
    category: str, actual_func, expected_counts: Dict[str, int], log=False
):
    actual_counts = Counter(map(actual_func, EMOJI_CATALOG.values()))
    if log:
        print(
            f"Checking {category} counts ({sum(expected_counts.values())} expected total)"
        )
    for name, actual in actual_counts.items():
        expected = expected_counts[name]
        assert (
            expected == actual
        ), f"Expected {expected} for {category} {name}, got {actual} instead."
        if log:
            print(f"  {name} : {actual}")


def main():
    given_group_counts = PARSED_EMOJI_METADATA[1]
    given_group_total = sum(given_group_counts.values())
    given_status_counts = PARSED_EMOJI_METADATA[2]
    given_status_total = sum(given_status_counts.values())
    assert given_group_total == given_status_total, (
        "Given status and group counts do not match: "
        f"{given_group_total} groups and {given_status_total} statuses"
    )
    check_counts("group", lambda x: x.group, given_group_counts, True)
    check_counts("status", lambda x: x.status, given_status_counts, True)
    print(f"Metadata for {len(EMOJI_CATALOG.keys())} entries parsed.")


if __name__ == "__main__":
    main()
