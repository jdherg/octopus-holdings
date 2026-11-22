from html.parser import HTMLParser
import struct
import unittest
from urllib.parse import urlparse

import octopusholdings
import emoji.renderer as renderer

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class MetaTagParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta = {}

    def handle_starttag(self, tag, attrs):
        if tag != "meta":
            return
        attr_map = dict(attrs)
        key = attr_map.get("property") or attr_map.get("name")
        if key and "content" in attr_map:
            self.meta[key] = attr_map["content"]


def parse_meta_tags(html_bytes: bytes):
    parser = MetaTagParser()
    parser.feed(html_bytes.decode("utf-8"))
    return parser.meta


def parse_png_dimensions(png_bytes: bytes):
    assert png_bytes[:8] == PNG_SIGNATURE
    return struct.unpack(">II", png_bytes[16:24])


class TestOctopusHoldingsApp(unittest.TestCase):
    def setUp(self):
        self.client = octopusholdings.app.test_client()

    def test_root_html_has_social_card_meta_tags(self):
        resp = self.client.get(
            "/",
            headers={"X-Forwarded-Proto": "https", "Host": "octopus.holdings"},
        )
        self.assertEqual(resp.status_code, 200)
        meta = parse_meta_tags(resp.data)
        self.assertEqual(meta["og:type"], "website")
        self.assertEqual(meta["og:site_name"], "Octopus Holdings")
        self.assertEqual(meta["og:url"], "https://octopus.holdings/")
        self.assertEqual(
            meta["og:image"], "https://octopus.holdings/tada/octopus.png?card=1"
        )
        self.assertEqual(meta["og:image:type"], "image/png")
        self.assertEqual(meta["og:image:width"], str(renderer.SOCIAL_CARD_WIDTH))
        self.assertEqual(meta["og:image:height"], str(renderer.SOCIAL_CARD_HEIGHT))
        self.assertEqual(meta["twitter:card"], "summary_large_image")
        self.assertEqual(meta["twitter:image"], meta["og:image"])
        self.assertIn("party popper", meta["og:description"])
        self.assertIn("octopus", meta["og:description"])

    def test_direct_png_endpoint_natural_aspect_ratio(self):
        resp = self.client.get("/tada.png")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.mimetype, "image/png")
        self.assertEqual(resp.headers.get("Cache-Control"), "public, max-age=86400")
        self.assertEqual(parse_png_dimensions(resp.data), (256, 440))

    def test_direct_png_endpoint_multi_emoji_stack(self):
        resp = self.client.get("/coffee/tada/rocket/octopus.png")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.mimetype, "image/png")
        self.assertEqual(parse_png_dimensions(resp.data), (256, 808))

    def test_social_card_png_endpoint(self):
        resp = self.client.get("/coffee/tada/rocket/octopus.png?card=1")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.mimetype, "image/png")
        self.assertEqual(
            parse_png_dimensions(resp.data),
            (renderer.SOCIAL_CARD_WIDTH, renderer.SOCIAL_CARD_HEIGHT),
        )

    def test_og_image_url_fetches_valid_card_png(self):
        html_resp = self.client.get(
            "/noto_2/wave:skin-tone-medium/rc",
            headers={"X-Forwarded-Proto": "https", "Host": "octopus.holdings"},
        )
        self.assertEqual(html_resp.status_code, 200)
        meta = parse_meta_tags(html_resp.data)
        parsed = urlparse(meta["og:image"])
        self.assertEqual(parsed.scheme, "https")
        self.assertEqual(parsed.netloc, "octopus.holdings")

        img_resp = self.client.get(f"{parsed.path}?{parsed.query}")
        self.assertEqual(img_resp.status_code, 200)
        self.assertEqual(img_resp.mimetype, "image/png")
        self.assertEqual(
            parse_png_dimensions(img_resp.data),
            (renderer.SOCIAL_CARD_WIDTH, renderer.SOCIAL_CARD_HEIGHT),
        )

    def test_custom_emoji_unicode_alias_preserves_custom_resolution(self):
        # ❤️ maps to custom pink_heart, not noto red heart.
        html_resp = self.client.get(
            "/❤️",
            headers={"X-Forwarded-Proto": "https", "Host": "octopus.holdings"},
        )
        self.assertEqual(html_resp.status_code, 200)
        meta = parse_meta_tags(html_resp.data)
        self.assertEqual(
            meta["og:image"], "https://octopus.holdings/pink_heart/octopus.png?card=1"
        )

    def test_random_html_emits_deterministic_og_image(self):
        html_resp = self.client.get(
            "/noto_2/random",
            headers={"X-Forwarded-Proto": "https", "Host": "octopus.holdings"},
        )
        self.assertEqual(html_resp.status_code, 200)
        meta = parse_meta_tags(html_resp.data)
        self.assertNotIn("random", meta["og:image"])
        parsed = urlparse(meta["og:image"])
        img_resp = self.client.get(f"{parsed.path}?{parsed.query}")
        self.assertEqual(img_resp.status_code, 200)
        self.assertEqual(img_resp.mimetype, "image/png")

    def test_random_png_disables_caching(self):
        resp = self.client.get("/random.png")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.mimetype, "image/png")
        self.assertEqual(resp.headers.get("Cache-Control"), "no-store")

    def test_oversized_stack_rejected_for_png_but_safe_for_html(self):
        long_path = "/".join(["octopus"] * (renderer.MAX_RENDER_STACK_LENGTH + 1))
        png_resp = self.client.get(f"/{long_path}.png")
        self.assertEqual(png_resp.status_code, 400)

        html_resp = self.client.get(f"/{long_path}")
        self.assertEqual(html_resp.status_code, 200)
        meta = parse_meta_tags(html_resp.data)
        self.assertNotIn("og:image", meta)
        self.assertEqual(meta["twitter:card"], "summary")

    def test_existing_emoji_svg_route_unchanged(self):
        resp = self.client.get("/emoji/emoji_rc.svg")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"<svg", resp.data)
        resp.close()

        missing = self.client.get("/emoji/does_not_exist/foo.svg")
        self.assertEqual(missing.status_code, 404)
