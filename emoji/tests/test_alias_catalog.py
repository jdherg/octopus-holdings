import unittest

from emoji.alias_catalog import (
    ALIASES_TO_EMOJI,
    derive_codepoint_aliases,
    derive_skin_tone_aliases,
)


class TestCodepointDeriver(unittest.TestCase):
    def test_single_codepoint(self):
        octopus = "🐙"
        aliases = derive_codepoint_aliases(octopus)
        self.assertIn(octopus, aliases)
        self.assertIn("1f419", aliases)
        self.assertIn("u1f419", aliases)


class TestSkinToneDeriver(unittest.TestCase):
    def test_single(self):
        aliases = derive_skin_tone_aliases("👋", "wave")
        self.assertIn("wave:skin-tone-medium", aliases)

    def test_double(self):
        aliases = derive_skin_tone_aliases("🧑‍🤝‍🧑", "couple")
        self.assertIn("couple:skin-tone-light:skin-tone-light", aliases)


class TestAliasesToEmoji(unittest.TestCase):
    def test_octopus(self):
        self.assertEqual(ALIASES_TO_EMOJI["octopus"], "🐙")

    def test_wave(self):
        self.assertEqual(ALIASES_TO_EMOJI.get("wave"), "👋")
        self.assertEqual(ALIASES_TO_EMOJI.get("wave:skin-tone-medium"), "👋🏽")
