import os
from typing import List, Optional, Sequence, Tuple
from flask import (
    abort,
    Flask,
    render_template,
    request,
    Response,
    send_from_directory,
    url_for,
)
from werkzeug.middleware.proxy_fix import ProxyFix

from emoji.emoji_catalog import EMOJI_CATALOG
import emoji.emoji_resolver as emoji_resolver
import emoji.renderer as renderer

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
OCTOPUS_HOLDINGS_ENV = os.environ.get("OCTOPUS_HOLDINGS_ENV")

TRUTHY_QUERY_VALUES = {"1", "true", "yes"}
MAX_TITLE_EMOJI = 8
MAX_DESCRIPTION_LENGTH = 160


def _canonical_token(token: str) -> str:
    resolved = emoji_resolver.resolve_alias(token)
    if resolved is None:
        return "question"
    if resolved.isascii():
        return resolved
    if token.isascii() and not any(ch in token for ch in "?#% \t\r\n"):
        return token
    return "-".join(hex(ord(ch))[2:].lower() for ch in resolved)


def _build_canonical_emojicode(
    processed_stack: Sequence[Tuple[str, Optional[str]]],
) -> str:
    segments: List[str] = []
    last_set: Optional[str] = None
    for token, desired_set in processed_stack:
        if desired_set is not None and desired_set != last_set:
            segments.append(desired_set)
            last_set = desired_set
        segments.append(_canonical_token(token))
    return "/".join(segments)


def resolve_emojicode(
    emojicode: str,
) -> Tuple[List[Tuple[str, Optional[str]]], List[str], str, bool]:
    in_stack = emojicode.split("/")
    current_desired_set = None
    processed_stack: List[Tuple[str, Optional[str]]] = []
    has_random = False
    # Process commands. (Just desired emoji set for now.)
    for token in in_stack:
        if emoji_resolver.is_emoji_set(token):
            current_desired_set = token
        else:
            if token == "random":
                has_random = True
                token = emoji_resolver.random_emoji()
            processed_stack.append((token, current_desired_set))
    # Fill in defaults.
    if not processed_stack:
        processed_stack.append(("tada", current_desired_set))
    if len(processed_stack) == 1:
        processed_stack.append(("octopus", current_desired_set))
    # Turn it into paths.
    emojistack = [
        emoji_resolver.resolve(alias, desired_set)
        for alias, desired_set in processed_stack
    ]
    canonical_emojicode = _build_canonical_emojicode(processed_stack)
    return processed_stack, emojistack, canonical_emojicode, has_random


def describe_stack(
    processed_stack: Sequence[Tuple[str, Optional[str]]], site_name: str
) -> Tuple[str, str, str]:
    symbols: List[str] = []
    names: List[str] = []
    all_unicode = True
    for alias, _desired_set in processed_stack:
        resolved_emoji = emoji_resolver.resolve_alias(
            alias
        ) or emoji_resolver.resolve_alias("question")
        record = EMOJI_CATALOG.get(resolved_emoji)
        if record:
            symbols.append(record.literal)
            names.append(record.name)
        else:
            all_unicode = False
            label = resolved_emoji.replace("_", " ")
            symbols.append(label)
            names.append(label)

    display_symbols = symbols[:MAX_TITLE_EMOJI]
    separator = "" if all_unicode else " "
    summary = separator.join(display_symbols)
    if len(symbols) > MAX_TITLE_EMOJI:
        summary += "…"
    og_title = f"{summary} — {site_name}" if summary else site_name

    description = ", ".join(names)
    if len(description) > MAX_DESCRIPTION_LENGTH:
        suffix = f", … ({len(names)} emoji)"
        cutoff = MAX_DESCRIPTION_LENGTH - len(suffix)
        trimmed = description[:cutoff].rsplit(", ", 1)[0]
        description = f"{trimmed}{suffix}"

    og_image_alt = f"Emoji stack: {description}"
    return og_title, description, og_image_alt


@app.route("/emoji/<path:filepath>")
def emoji_src(filepath):
    resolved = emoji_resolver.resolve_to_internal_path(filepath)
    if resolved:
        path, base = resolved
        return send_from_directory(path, base)
    abort(404)


@app.route("/<path:emojicode>.png")
def show_emoji_png(emojicode):
    _processed_stack, emojistack, _canonical, has_random = resolve_emojicode(emojicode)
    if len(emojistack) > renderer.MAX_RENDER_STACK_LENGTH:
        abort(400)
    card = request.args.get("card", "").lower() in TRUTHY_QUERY_VALUES
    png_bytes, _width, _height = renderer.render_png(emojistack, card=card)
    response = Response(png_bytes, mimetype="image/png")
    if has_random:
        response.headers["Cache-Control"] = "no-store"
    else:
        response.headers["Cache-Control"] = "public, max-age=86400"
    return response


@app.route("/")
@app.route("/<path:emojicode>")
def show_emoji(emojicode="tada"):
    processed_stack, emojistack, canonical_emojicode, _has_random = resolve_emojicode(
        emojicode
    )
    site_name = (
        f"{OCTOPUS_HOLDINGS_ENV} Octopus Holdings"
        if OCTOPUS_HOLDINGS_ENV and OCTOPUS_HOLDINGS_ENV != "PROD"
        else "Octopus Holdings"
    )
    og_title, og_description, og_image_alt = describe_stack(processed_stack, site_name)

    og_image = None
    og_image_width = None
    og_image_height = None
    if len(emojistack) <= renderer.MAX_RENDER_STACK_LENGTH:
        og_image = url_for(
            "show_emoji_png",
            emojicode=canonical_emojicode,
            card=1,
            _external=True,
        )
        og_image_width = renderer.SOCIAL_CARD_WIDTH
        og_image_height = renderer.SOCIAL_CARD_HEIGHT

    return render_template(
        "index.html",
        stack=emojistack,
        env=OCTOPUS_HOLDINGS_ENV,
        site_name=site_name,
        og_title=og_title,
        og_description=og_description,
        og_url=request.base_url,
        og_image=og_image,
        og_image_width=og_image_width,
        og_image_height=og_image_height,
        og_image_alt=og_image_alt,
    )


if __name__ == "__main__":
    if not OCTOPUS_HOLDINGS_ENV:
        OCTOPUS_HOLDINGS_ENV = "LOCAL"
    app.debug = True
    app.run()
