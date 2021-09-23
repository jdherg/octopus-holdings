import unittest

from emoji.alias_catalog import ALIASES_TO_EMOJI, derive_codepoint_aliases


class TestCodepointDeriver(unittest.TestCase):
    def test_single_codepoint(self):
        octopus = "🐙"
        aliases = derive_codepoint_aliases(octopus)
        self.assertIn(octopus, aliases)
        self.assertIn("1f419", aliases)
        self.assertIn("u1f419", aliases)


class TestAliasesToEmoji(unittest.TestCase):
    def test_octopus(self):
        self.assertEqual(ALIASES_TO_EMOJI["octopus"], "🐙")
