from collections import Counter
import unittest

from emoji.emoji_catalog import (
    EMOJI_CATALOG,
    EMOJI_VARIANTS,
    PARSED_EMOJI_METADATA,
    Emoji,
)

GROUP_COUNTS = PARSED_EMOJI_METADATA[1]
STATUS_COUNTS = PARSED_EMOJI_METADATA[2]


class TestEmojiTestFileParsing(unittest.TestCase):
    def test_group_and_status_comparison(self):
        expected_group_total = sum(GROUP_COUNTS.values())
        expected_status_total = sum(STATUS_COUNTS.values())
        self.assertEqual(expected_group_total, expected_status_total)

    def test_group_counts(self):
        actual_group_counts = Counter([e.group for e in EMOJI_CATALOG.values()])
        for group, expected_count in GROUP_COUNTS.items():
            self.assertEqual(
                expected_count, actual_group_counts[group], f"Group: {group}"
            )

    def test_status_counts(self):
        actual_status_counts = Counter([e.status for e in EMOJI_CATALOG.values()])
        for status, expected_count in STATUS_COUNTS.items():
            self.assertEqual(
                expected_count, actual_status_counts[status], f"Status: {status}"
            )

    def test_uniqueness(self):
        self.assertEqual(len(EMOJI_CATALOG.keys()), len(set(EMOJI_CATALOG.keys())))


class TestEmojiRecords(unittest.TestCase):
    def test_basic_emoji_record(self):
        octopus = EMOJI_CATALOG["🐙"]
        self.assertEqual(
            octopus,
            Emoji(
                literal="🐙",
                name="octopus",
                code_points=["1F419"],
                status="fully-qualified",
                group="Animals & Nature",
                subgroup="animal-marine",
                version="0.6",
            ),
        )


class TestVariants(unittest.TestCase):
    def test_wave(self):
        wave = "👋"
        self.assertIn(wave, EMOJI_VARIANTS)
