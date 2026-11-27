#!/usr/bin/env python3
"""Draw a one-page newspaper front page summing up the world news of
Friday 27 November 2026, and write it to /output/entry.png.

Pure Python 3 stdlib, no network, fully deterministic: the same bytes
come out of every run. Bitmap font and PNG encoder are hand-rolled.
"""
import os
import struct
import zlib

W, H = 1024, 1024
PAPER = (247, 243, 232)
INK = (17, 17, 17)
RED = (176, 32, 32)
BLUE = (30, 74, 122)
GREY = (110, 104, 90)
LIGHT = (232, 226, 210)

# ---------------------------------------------------------------- font
# 5x7 bitmap font: each glyph is 7 rows, each row a 5-bit mask.
FONT = {
    'A': (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'B': (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    'C': (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    'D': (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    'E': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    'F': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    'G': (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    'H': (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'I': (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    'J': (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    'K': (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    'L': (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    'M': (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    'N': (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    'O': (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'P': (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    'Q': (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    'R': (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    'S': (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    'T': (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    'U': (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'V': (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    'W': (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    'X': (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    'Y': (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    'Z': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    '0': (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    '1': (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    '2': (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    '3': (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    '4': (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    '5': (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    '6': (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    '7': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    '8': (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    '9': (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    ' ': (0, 0, 0, 0, 0, 0, 0),
    '.': (0, 0, 0, 0, 0, 0x0C, 0x0C),
    ',': (0, 0, 0, 0, 0x0C, 0x04, 0x08),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    '-': (0, 0, 0, 0x0E, 0, 0, 0),
    ':': (0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0),
    ';': (0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08),
    '!': (0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04),
    '?': (0x0E, 0x11, 0x01, 0x02, 0x04, 0, 0x04),
    '(': (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ')': (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    '/': (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    '&': (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    '$': (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    '%': (0x19, 0x1A, 0x02, 0x04, 0x08, 0x0B, 0x13),
    '+': (0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0),
    '=': (0, 0, 0x1F, 0, 0x1F, 0, 0),
    '"': (0x0A, 0x0A, 0, 0, 0, 0, 0),
    '*': (0, 0x04, 0x15, 0x0E, 0x15, 0x04, 0),
    '#': (0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A),
}

# ---------------------------------------------------------------- canvas
canvas = [[PAPER for _ in range(W)] for _ in range(H)]


def rect(x, y, w, h, color):
    for yy in range(max(0, y), min(H, y + h)):
        row = canvas[yy]
        for xx in range(max(0, x), min(W, x + w)):
            row[xx] = color


def hline(x, y, w, color, thick=1):
    rect(x, y, w, thick, color)


def vline(x, y, h, color, thick=1):
    rect(x, y, thick, h, color)


def outline(x, y, w, h, color, thick=1):
    hline(x, y, w, color, thick)
    hline(x, y + h - thick, w, color, thick)
    vline(x, y, h, color, thick)
    vline(x + w - thick, y, h, color, thick)


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(x, y, s, scale, color):
    cx = x
    for ch in s:
        glyph = FONT.get(ch.upper(), FONT[' '])
        for r in range(7):
            bits = glyph[r]
            for c in range(5):
                if bits & (1 << (4 - c)):
                    rect(cx + c * scale, y + r * scale, scale, scale, color)
        cx += 6 * scale
    return cx


def draw_centered(y, s, scale, color):
    draw_text((W - text_width(s, scale)) // 2, y, s, scale, color)


def wrap(s, scale, max_w):
    """Split text into lines that fit max_w pixels."""
    words = s.split(' ')
    lines, cur = [], ''
    for word in words:
        trial = word if not cur else cur + ' ' + word
        if text_width(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_para(x, y, s, scale, max_w, color, leading=4):
    lines = wrap(s, scale, max_w)
    for i, line in enumerate(lines):
        draw_text(x, y + i * (7 * scale + leading), line, scale, color)
    return y + len(lines) * (7 * scale + leading)


# ---------------------------------------------------------------- icons
def draw_ballot_box(x, y, w, h):
    """A ballot box with a paper slip going in."""
    outline(x, y + 60, w, h - 60, INK, 3)
    # slot
    rect(x + w // 4, y + 60, w // 2, 6, INK)
    # paper slip above the slot
    rect(x + w // 2 - 34, y + 6, 68, 62, (255, 255, 255))
    outline(x + w // 2 - 34, y + 6, 68, 62, INK, 2)
    rect(x + w // 2 - 22, y + 18, 44, 4, RED)
    rect(x + w // 2 - 22, y + 30, 44, 4, INK)
    rect(x + w // 2 - 22, y + 42, 30, 4, INK)
    # big check mark on the box
    for i in range(26):
        rect(x + 52 + i * 2, y + 130 + i * 2, 6, 6, RED)
        rect(x + 52 + 52 + i * 2, y + 182 - i * 2, 6, 6, RED)
    # "VOTE" label on the box
    draw_text(x + (w - text_width('VOTE', 3)) // 2, y + h - 52, 'VOTE', 3, INK)


def draw_bolt(x, y, s, color):
    """Lightning bolt polygon drawn as stacked bars."""
    bars = [(3, 0, 4), (2, 1, 5), (1, 2, 6), (0, 3, 7),
            (2, 4, 5), (4, 5, 3), (3, 6, 4), (2, 7, 5),
            (1, 8, 6), (0, 9, 7), (2, 10, 4), (4, 11, 2)]
    for bx, by, bw in bars:
        rect(x + bx * s, y + by * s, bw * s, s, color)


def draw_bag(x, y, w, h):
    outline(x, y + 26, w, h - 26, BLUE, 3)
    # handles
    rect(x + w // 4 - 4, y, 8, 34, BLUE)
    rect(x + 3 * w // 4 - 4, y, 8, 34, BLUE)
    rect(x + w // 4 - 4, y, w // 2 + 8, 8, BLUE)
    # sale tag
    draw_text(x + (w - text_width('SALE', 3)) // 2, y + h // 2, 'SALE', 3, RED)


def draw_gavel(x, y, s, color):
    rect(x, y, 10 * s, 3 * s, color)
    rect(x + 2 * s, y + 3 * s, 2 * s, 6 * s, color)
    rect(x, y + 9 * s, 10 * s, 2 * s, color)


# ---------------------------------------------------------------- page
def build():
    # --- masthead
    draw_centered(26, 'THE WORLD TODAY', 7, INK)
    hline(36, 92, W - 72, INK, 3)
    draw_centered(104, 'FRIDAY, 27 NOVEMBER 2026', 3, RED)
    draw_centered(132, "THE DAY'S WORLD NEWS - ONE PAGE", 2, GREY)
    hline(36, 158, W - 72, INK, 5)

    # --- lead story: New Zealand final count
    draw_text(36, 176, 'WELLINGTON  -  ELECTION', 2, RED)
    draw_text(36, 200, 'FINAL COUNT TO', 4, INK)
    draw_text(36, 234, 'SETTLE NEW ZEALAND', 4, INK)
    draw_para(36, 276,
              'New Zealand releases its final election count today, with about '
              '400,000 special votes to settle whether the incumbent '
              'centre-right coalition keeps its razor-slim majority of two seats.',
              2, 600, INK)
    draw_para(36, 372,
              'Preliminary results after the 7 November vote left the '
              'three-party coalition led by National two seats ahead. The '
              'official tally decides the shape of parliament.',
              2, 600, GREY)
    draw_ballot_box(700, 186, 288, 250)

    hline(36, 452, W - 72, INK, 2)

    # --- two columns: Ukraine / Duterte
    draw_text(36, 470, 'UKRAINE BRACES', 3, INK)
    draw_bolt(462, 464, 3, RED)
    draw_para(36, 500,
              'President Zelenskyy warns Russia is preparing a major new attack '
              'on Ukraine power grid, as repair crews work in six regions '
              'hit by missiles and drones overnight.',
              2, 420, INK)

    vline(508, 470, 190, INK, 2)

    draw_text(536, 470, 'DUTERTE TO FACE ICC', 3, INK)
    draw_gavel(918, 466, 3, BLUE)
    draw_para(536, 500,
              'Former Philippine president Rodrigo Duterte goes on trial in The '
              'Hague on Monday over alleged crimes against humanity during his '
              'six-year drug war. Families of victims seek justice.',
              2, 452, INK)

    hline(36, 676, W - 72, INK, 2)

    # --- Black Friday band
    draw_bag(56, 700, 96, 110, )
    draw_text(188, 700, 'BLACK FRIDAY, WITH CARE', 3, INK)
    draw_para(188, 734,
              'US shoppers head out for Black Friday as inflation bites. Holiday '
              'sales are forecast above $1 trillion, up 4.2% on last year, but '
              'retailers warn of strain beneath the headline.',
              2, 780, INK)

    hline(36, 830, W - 72, INK, 2)

    # --- Also Today strip
    draw_text(36, 848, 'ALSO TODAY', 2, RED)
    items = [
        ('Poundland collapses;', '11,000 jobs at risk'),
        ('Norse Atlantic halts', 'all flights'),
        ('Tanker capsizes off', 'Ibiza; one dead'),
        ("Macy parade moves", 'to Saturday'),
        ('UK net migration falls', 'to 77,000'),
        ('Depardieu to stand', 'trial for rape'),
    ]
    col_w = (W - 72) // 3
    for i, (l1, l2) in enumerate(items):
        cx = 36 + (i % 3) * col_w
        cy = 880 + (i // 3) * 52
        draw_text(cx, cy, l1, 2, INK)
        draw_text(cx, cy + 20, l2, 2, INK)

    # --- footer
    hline(36, 972, W - 72, INK, 2)
    draw_centered(984, 'SOURCES: REUTERS - AP - BBC  |  FRIDAY 27 NOVEMBER 2026', 2, GREY)


def png_bytes():
    raw = bytearray()
    for row in canvas:
        raw.append(0)  # filter: none
        for r, g, b in row:
            raw += bytes((r, g, b))
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        c = struct.pack('>I', len(data)) + tag + data
        return c + struct.pack('>I', zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr)
            + chunk(b'IDAT', comp) + chunk(b'IEND', b''))


def main():
    build()
    out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, 'entry.png')
    with open(path, 'wb') as f:
        f.write(png_bytes())
    print('wrote', path)


if __name__ == '__main__':
    main()
