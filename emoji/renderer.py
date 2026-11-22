import functools
import os
import pathlib
from typing import Optional, Sequence, Tuple
from xml.sax.saxutils import quoteattr

import resvg_py

import emoji.emoji_resolver as emoji_resolver

EMOJI_SIZE = 128
STACK_STEP = 92

DIRECT_IMAGE_SCALE = 2.0
DIRECT_IMAGE_MAX_DIM = 1200

SOCIAL_CARD_WIDTH = 1200
SOCIAL_CARD_HEIGHT = 630
SOCIAL_CARD_PADDING = 40
SOCIAL_CARD_BACKGROUND: Optional[str] = None

MAX_RENDER_STACK_LENGTH = 64

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


def composition_dimensions(stack_length: int) -> Tuple[int, int]:
    if stack_length < 1:
        raise ValueError("stack_length must be at least 1")
    return EMOJI_SIZE, EMOJI_SIZE + STACK_STEP * (stack_length - 1)


def fit_dimensions(
    content_width: int,
    content_height: int,
    scale: float = DIRECT_IMAGE_SCALE,
    max_dim: int = DIRECT_IMAGE_MAX_DIM,
) -> Tuple[int, int]:
    """Scale content dimensions while capping the longest edge and preserving aspect ratio."""
    if content_width <= 0 or content_height <= 0:
        raise ValueError("content dimensions must be positive")
    effective_scale = min(scale, max_dim / content_width, max_dim / content_height)
    width = max(1, round(content_width * effective_scale))
    height = max(1, round(content_height * effective_scale))
    return width, height


def contain_rect(
    content_width: int,
    content_height: int,
    canvas_width: int,
    canvas_height: int,
    padding: int = 0,
) -> Tuple[float, float, float, float]:
    """Compute centered (x, y, width, height) that fits arbitrary aspect ratios without cropping."""
    if content_width <= 0 or content_height <= 0:
        raise ValueError("content dimensions must be positive")
    avail_width = canvas_width - 2 * padding
    avail_height = canvas_height - 2 * padding
    if avail_width <= 0 or avail_height <= 0:
        raise ValueError("canvas dimensions must exceed twice the padding")
    scale = min(avail_width / content_width, avail_height / content_height)
    draw_width = content_width * scale
    draw_height = content_height * scale
    offset_x = (canvas_width - draw_width) / 2.0
    offset_y = (canvas_height - draw_height) / 2.0
    return offset_x, offset_y, draw_width, draw_height


def build_composition_svg(
    internal_paths: Sequence[str],
    canvas_width: int,
    canvas_height: int,
    padding: int = 0,
    background: Optional[str] = None,
) -> str:
    content_width, content_height = composition_dimensions(len(internal_paths))
    offset_x, offset_y, draw_width, draw_height = contain_rect(
        content_width,
        content_height,
        canvas_width,
        canvas_height,
        padding=padding,
    )
    images = "\n".join(
        f'    <image x="0" y="{STACK_STEP * i}" width="{EMOJI_SIZE}" height="{EMOJI_SIZE}" '
        f"xlink:href={quoteattr(path)}/>"
        for i, path in enumerate(internal_paths)
    )
    bg_rect = (
        f'  <rect width="100%" height="100%" fill={quoteattr(background)}/>\n'
        if background
        else ""
    )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{canvas_width}" height="{canvas_height}" '
        f'viewBox="0 0 {canvas_width} {canvas_height}">\n'
        f"{bg_rect}"
        f'  <svg x="{offset_x:.3f}" y="{offset_y:.3f}" '
        f'width="{draw_width:.3f}" height="{draw_height:.3f}" '
        f'viewBox="0 0 {content_width} {content_height}" '
        'preserveAspectRatio="xMidYMid meet">\n'
        f"{images}\n"
        "  </svg>\n"
        "</svg>"
    )


def _resolve_internal_paths(emoji_paths: Sequence[str]) -> Tuple[str, ...]:
    internal_paths = []
    for external_path in emoji_paths:
        resolved = emoji_resolver.resolve_to_internal_path(external_path)
        if not resolved:
            raise ValueError(f"Unresolvable emoji path: {external_path}")
        folder, filename = resolved
        internal_paths.append(os.path.join(folder, filename))
    return tuple(internal_paths)


@functools.lru_cache(maxsize=128)
def _render_png_cached(
    emoji_paths: Tuple[str, ...], card: bool
) -> Tuple[bytes, int, int]:
    internal_paths = _resolve_internal_paths(emoji_paths)
    if card:
        canvas_width = SOCIAL_CARD_WIDTH
        canvas_height = SOCIAL_CARD_HEIGHT
        padding = SOCIAL_CARD_PADDING
        background: Optional[str] = SOCIAL_CARD_BACKGROUND
    else:
        content_width, content_height = composition_dimensions(len(internal_paths))
        canvas_width, canvas_height = fit_dimensions(content_width, content_height)
        padding = 0
        background = None

    svg = build_composition_svg(
        internal_paths,
        canvas_width=canvas_width,
        canvas_height=canvas_height,
        padding=padding,
        background=background,
    )
    png_bytes = resvg_py.svg_to_bytes(
        svg_string=svg,
        resources_dir=str(REPO_ROOT),
        skip_system_fonts=True,
    )
    return png_bytes, canvas_width, canvas_height


def render_png(
    emoji_paths: Sequence[str], card: bool = False
) -> Tuple[bytes, int, int]:
    """Render resolved emoji SVG paths into a PNG image.

    When card=False, returns a transparent PNG sized to the composition's natural
    aspect ratio (bounded by DIRECT_IMAGE_MAX_DIM).
    When card=True, returns a 1200x630 social card PNG with the composition centered
    and fitted without cropping.
    """
    if not emoji_paths:
        raise ValueError("emoji_paths must not be empty")
    if len(emoji_paths) > MAX_RENDER_STACK_LENGTH:
        raise ValueError(
            f"stack length {len(emoji_paths)} exceeds maximum of {MAX_RENDER_STACK_LENGTH}"
        )
    return _render_png_cached(tuple(emoji_paths), card)
