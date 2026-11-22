import struct
import unittest

import emoji.emoji_resolver as emoji_resolver
import emoji.renderer as renderer

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def parse_png_ihdr(png_bytes: bytes):
    """Return (width, height, color_type) from a PNG's IHDR chunk."""
    assert png_bytes[:8] == PNG_SIGNATURE
    assert png_bytes[12:16] == b"IHDR"
    width, height = struct.unpack(">II", png_bytes[16:24])
    color_type = png_bytes[25]
    return width, height, color_type


class TestGeometry(unittest.TestCase):
    def test_composition_dimensions(self):
        self.assertEqual(renderer.composition_dimensions(1), (128, 128))
        self.assertEqual(renderer.composition_dimensions(2), (128, 220))
        self.assertEqual(renderer.composition_dimensions(3), (128, 312))
        self.assertEqual(renderer.composition_dimensions(10), (128, 956))

    def test_composition_dimensions_invalid(self):
        with self.assertRaises(ValueError):
            renderer.composition_dimensions(0)

    def test_fit_dimensions_standard_portrait(self):
        # 2-emoji stack fits comfortably at default 2x scale.
        self.assertEqual(renderer.fit_dimensions(128, 220), (256, 440))

    def test_fit_dimensions_clamps_tall_stack_preserving_aspect_ratio(self):
        # 10-emoji stack (128x956) exceeds max_dim=1200 at 2x, so it scales down cleanly.
        w, h = renderer.fit_dimensions(128, 956, scale=2.0, max_dim=1200)
        self.assertEqual(h, 1200)
        self.assertAlmostEqual(w / h, 128 / 956, places=2)

    def test_fit_dimensions_clamps_wide_composition_preserving_aspect_ratio(self):
        w, h = renderer.fit_dimensions(956, 128, scale=2.0, max_dim=1200)
        self.assertEqual((w, h), (1200, 161))
        self.assertAlmostEqual(h / w, 128 / 956, places=2)

    def test_fit_dimensions_square(self):
        self.assertEqual(renderer.fit_dimensions(128, 128), (256, 256))

    def test_contain_rect_tall_in_landscape_card(self):
        x, y, w, h = renderer.contain_rect(128, 220, 1200, 630, padding=40)
        self.assertAlmostEqual(h, 550.0, places=3)
        self.assertAlmostEqual(w / h, 128 / 220, places=4)
        self.assertAlmostEqual(y, 40.0, places=3)
        self.assertAlmostEqual(x, (1200 - w) / 2.0, places=3)

    def test_contain_rect_very_tall_in_landscape_card(self):
        x, y, w, h = renderer.contain_rect(128, 956, 1200, 630, padding=40)
        self.assertAlmostEqual(h, 550.0, places=3)
        self.assertAlmostEqual(w / h, 128 / 956, places=4)
        self.assertGreaterEqual(x, 40.0)
        self.assertAlmostEqual(y, 40.0, places=3)

    def test_contain_rect_wide_in_landscape_card(self):
        x, y, w, h = renderer.contain_rect(956, 128, 1200, 630, padding=40)
        self.assertAlmostEqual(w, 1120.0, places=3)
        self.assertAlmostEqual(w / h, 956 / 128, places=4)
        self.assertAlmostEqual(x, 40.0, places=3)
        self.assertGreaterEqual(y, 40.0)

    def test_contain_rect_square_in_landscape_card(self):
        x, y, w, h = renderer.contain_rect(128, 128, 1200, 630, padding=40)
        self.assertAlmostEqual(w, 550.0, places=3)
        self.assertAlmostEqual(h, 550.0, places=3)
        self.assertAlmostEqual(x, (1200 - 550) / 2.0, places=3)
        self.assertAlmostEqual(y, 40.0, places=3)


class TestRenderPng(unittest.TestCase):
    def test_render_direct_png_preserves_natural_aspect_ratio(self):
        stack = [
            emoji_resolver.resolve("tada"),
            emoji_resolver.resolve("octopus"),
        ]
        png_bytes, width, height = renderer.render_png(stack, card=False)
        self.assertEqual((width, height), (256, 440))
        ihdr_w, ihdr_h, color_type = parse_png_ihdr(png_bytes)
        self.assertEqual((ihdr_w, ihdr_h), (256, 440))
        # Direct PNG uses RGBA (color type 6) for transparent background.
        self.assertEqual(color_type, 6)

    def test_render_direct_png_tall_stack_bounded(self):
        stack = [emoji_resolver.resolve("tada")] * 9 + [
            emoji_resolver.resolve("octopus")
        ]
        png_bytes, width, height = renderer.render_png(stack, card=False)
        ihdr_w, ihdr_h, _ = parse_png_ihdr(png_bytes)
        self.assertEqual((ihdr_w, ihdr_h), (width, height))
        self.assertEqual(height, renderer.DIRECT_IMAGE_MAX_DIM)
        self.assertAlmostEqual(width / height, 128 / 956, places=2)

    def test_render_social_card_png_fixed_dimensions(self):
        for stack_len in (2, 4, 10):
            stack = [emoji_resolver.resolve("tada")] * (stack_len - 1) + [
                emoji_resolver.resolve("octopus")
            ]
            png_bytes, width, height = renderer.render_png(stack, card=True)
            self.assertEqual(
                (width, height),
                (renderer.SOCIAL_CARD_WIDTH, renderer.SOCIAL_CARD_HEIGHT),
            )
            ihdr_w, ihdr_h, color_type = parse_png_ihdr(png_bytes)
            self.assertEqual(
                (ihdr_w, ihdr_h),
                (renderer.SOCIAL_CARD_WIDTH, renderer.SOCIAL_CARD_HEIGHT),
            )
            # Social card PNG also uses RGBA (color type 6) for transparent background.
            self.assertEqual(color_type, 6)

    def test_render_across_all_emoji_sets(self):
        stack = [
            emoji_resolver.resolve("rc"),
            emoji_resolver.resolve("octopus", "noto_1"),
            emoji_resolver.resolve("octopus", "noto_2"),
            emoji_resolver.resolve("octopus", "twemoji_1"),
            emoji_resolver.resolve("octopus", "fxemoji"),
        ]
        png_bytes, width, height = renderer.render_png(stack, card=False)
        ihdr_w, ihdr_h, _ = parse_png_ihdr(png_bytes)
        self.assertEqual((ihdr_w, ihdr_h), (width, height))
        self.assertEqual((width, height), (256, 992))

    def test_render_empty_or_oversized_raises(self):
        with self.assertRaises(ValueError):
            renderer.render_png([])
        oversized = [emoji_resolver.resolve("octopus")] * (
            renderer.MAX_RENDER_STACK_LENGTH + 1
        )
        with self.assertRaises(ValueError):
            renderer.render_png(oversized)
