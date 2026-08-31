"""
Draw the MoneyMind app icon.

The existing icon carries the full lockup -- mark, "MONEYMIND" wordmark
and a four-word tagline. At 1024px that reads fine. At 32px, the size a
browser tab actually renders, the bottom third collapses into an
unreadable smudge and the mark itself is squeezed into the top half.

An app icon is a mark, not a lockup. These drop the text entirely and
let the mark fill the frame, keeping the sampled brand colours so the
identity still reads as MoneyMind: navy #022655 to green #4AB743.

Rendered at 8x and downsampled with LANCZOS, so the diagonals stay clean
at every size rather than aliasing at the small end.
"""

from PIL import Image, ImageDraw

NAVY = (0x02, 0x26, 0x55)
GREEN = (0x4A, 0xB7, 0x43)
WHITE = (0xFF, 0xFF, 0xFF)

S = 2048          # working canvas
SIZES = [32, 180, 192, 512, 1024]


def gradient(size, a, b):
    """Diagonal navy -> green, matching the original's sweep."""
    g = Image.new("RGB", (size, size))
    px = g.load()
    for y in range(size):
        for x in range(size):
            t = x / (size - 1)
            px[x, y] = (
                int(a[0] + (b[0] - a[0]) * t),
                int(a[1] + (b[1] - a[1]) * t),
                int(a[2] + (b[2] - a[2]) * t),
            )
    return g


def mark_mask(size):
    """
    The M, plus an open ring sweeping around it.

    The ring is broken at the lower left so it reads as motion rather
    than a closed circle, which is what the original's swoosh does.
    """
    m = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(m)

    # Open ring, broken at the bottom where the M's legs land
    inset = size * 0.085
    ring_w = int(size * 0.075)
    d.arc(
        [inset, inset, size - inset, size - inset],
        start=128, end=52,
        fill=255, width=ring_w,
    )

    # The M, drawn as a thick polyline so the joints stay clean
    x0, x1 = size * 0.285, size * 0.715
    top, bot = size * 0.335, size * 0.700
    valley = size * 0.585
    stroke = int(size * 0.115)

    d.line(
        [
            (x0, bot),
            (x0, top),
            (size * 0.5, valley),
            (x1, top),
            (x1, bot),
        ],
        fill=255, width=stroke, joint="curve",
    )

    # Round the four stroke ends so nothing looks chopped
    r = stroke / 2
    for cx, cy in [(x0, bot), (x0, top), (x1, top), (x1, bot), (size * 0.5, valley)]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)

    return m


def rounded_mask(size, radius_ratio=0.22):
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).rounded_rectangle(
        [0, 0, size - 1, size - 1],
        radius=int(size * radius_ratio),
        fill=255,
    )
    return m


def build(variant):
    grad = gradient(S, NAVY, GREEN)
    mark = mark_mask(S)
    ground = rounded_mask(S)

    if variant == "light":
        base = Image.new("RGB", (S, S), WHITE)
        base.paste(grad, (0, 0), mark)
    else:
        base = Image.new("RGB", (S, S), WHITE)
        base.paste(grad, (0, 0))
        solid = Image.new("RGB", (S, S), WHITE)
        base.paste(solid, (0, 0), mark)

    out = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    out.paste(base, (0, 0), ground)
    return out


if __name__ == "__main__":
    import sys
    from pathlib import Path

    dest = Path(sys.argv[1])
    dest.mkdir(parents=True, exist_ok=True)

    for variant in ("light", "solid"):
        art = build(variant)
        for s in SIZES:
            art.resize((s, s), Image.LANCZOS).save(
                dest / f"{variant}-{s}.png"
            )
        print(f"  {variant}: " + ", ".join(str(s) for s in SIZES))
