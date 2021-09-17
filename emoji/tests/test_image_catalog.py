import unittest

from emoji.image_catalog import IMAGE_CATALOGS


class TestAllSets(unittest.TestCase):
    def check_emoji(self, emoji):
        for name, mapping in IMAGE_CATALOGS.items():
            self.assertTrue(emoji in mapping, f"{name} does not contain {emoji}")

    def test_0_6_basic(self):
        self.check_emoji("🐙")

    def test_0_7_basic(self):
        self.check_emoji("🐈")

    def test_1_0_basic(self):
        self.check_emoji("🌞")

    def test_2_0_basic(self):
        self.check_emoji("🗨")


NO_LONGER_UPDATED = {"fxemoji", "noto_1"}


class TestModernSets(unittest.TestCase):
    def check_emoji(self, emoji):
        for name, mapping in IMAGE_CATALOGS.items():
            if name not in NO_LONGER_UPDATED:
                self.assertTrue(emoji in mapping, f"{name} does not contain {emoji}")

    def test_1_0_skin_tone(self):
        self.check_emoji("🖖🏽")

    def test_3_0_basic(self):
        self.check_emoji("🦑")

    def test_3_0_skin_tone(self):
        self.check_emoji("🤙🏽")

    def test_4_0_skin_tone(self):
        self.check_emoji("🛌🏽")

    def test_5_0_basic(self):
        self.check_emoji("🦔")

    def test_5_0_skin_tone(self):
        self.check_emoji("🤟🏽")

    def test_11_0_basic(self):
        self.check_emoji("🥰")

    def test_11_0_skin_tone(self):
        self.check_emoji("🦵🏽")


class TestAnySet(unittest.TestCase):
    def check_emoji(self, emoji):
        present = False
        for mapping in IMAGE_CATALOGS.values():
            present |= emoji in mapping
        self.assertTrue(present, f"{emoji} not in any set")

    def test_2_0_skin_tone(self):
        self.check_emoji("⛹🏽")

    def test_12_0_basic(self):
        self.check_emoji("🪁")

    def test_12_0_skin_tone(self):
        self.check_emoji("🦻🏽")

    def test_13_0_basic(self):
        self.check_emoji("🫂")

    def test_13_0_skin_tone(self):
        self.check_emoji("🥷🏽")

    def test_complex(self):
        self.check_emoji("👩🏽‍🤝‍👩🏿")
