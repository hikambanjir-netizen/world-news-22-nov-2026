#!/usr/bin/env python3
"""World news front page for Sunday 22 November 2026.

Pure-stdlib Python 3.13 entry for make.fun bounty news-image-20261122.
Draws a newspaper front page that sums up the day's world news and writes
it to /output/entry.png (1024x1024, deterministic, no network).

Stories (researched 22 Nov 2026, ~00:50 UTC, from BBC, Reuters/AP,
euronews, PBS/NPR, Times of India):
  1. Gulf: Iran hits US bases in Bahrain; tankers struck in the Strait of
     Hormuz; Trump seeks a "permanent" nuclear deal with Iran.
  2. Ukraine: Russia launches one of the war's biggest barrages - 400 drones
     and 110 missiles; missiles stray into Poland; 2 killed in Kryvyi Rih.
  3. Climate: COP31 talks in Antalya deadlocked over fossil fuels, past
     their deadline.
  4. Markets: AI stock sell-off - S&P 500 down 3.7%, Nikkei down 5.1%.
  5. Mexico: FBI most-wanted cartel boss "El Chapo Isidro" captured in
     Sinaloa; violence erupts, 11 killed.
  6. Peru: magnitude 6.9 earthquake shakes the Andes, felt in Lima; no
     casualties reported.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
INK = (20, 20, 20)
PAPER = (244, 239, 230)
NAVY = (11, 31, 58)
NAVY2 = (18, 46, 84)
GOLD = (201, 162, 39)
WHITE = (255, 255, 255)
CREAM = (250, 246, 238)
RED = (185, 28, 28)
DARKRED = (127, 29, 29)
GREEN = (22, 101, 52)
BLUE = (30, 64, 175)
SKY = (220, 233, 245)
GREY = (107, 114, 128)
DARKGREY = (55, 65, 81)
ORANGE = (234, 88, 12)
YELLOW = (250, 204, 21)
BROWN = (120, 53, 15)


# ------------------------------------------------------- 5x7 bitmap font
# Glyphs are 7 rows of 5 cells; '#' is ink. Uppercase, digits, punctuation.
FONT = {
    "A": (" ### ", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "B": ("#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "),
    "C": (" ####", "#    ", "#    ", "#    ", "#    ", "#    ", " ####"),
    "D": ("#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "),
    "E": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"),
    "F": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "),
    "G": (" ####", "#    ", "#    ", "# ###", "#   #", "#   #", " ### "),
    "H": ("#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "I": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "#####"),
    "J": ("  ###", "   # ", "   # ", "   # ", "   # ", "#  # ", " ##  "),
    "K": ("#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"),
    "L": ("#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"),
    "M": ("#   #", "## ##", "# # #", "# # #", "#   #", "#   #", "#   #"),
    "N": ("#   #", "##  #", "##  #", "# # #", "#  ##", "#  ##", "#   #"),
    "O": (" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "P": ("#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "),
    "Q": (" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## #"),
    "R": ("#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"),
    "S": (" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "),
    "T": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "),
    "U": ("#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "V": ("#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "),
    "W": ("#   #", "#   #", "#   #", "# # #", "# # #", "## ##", "#   #"),
    "X": ("#   #", "#   #", " # # ", "  #  ", " # # ", "#   #", "#   #"),
    "Y": ("#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "),
    "Z": ("#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"),
    "0": (" ### ", "#   #", "#  ##", "# # #", "##  #", "#   #", " ### "),
    "1": ("  #  ", " ##  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    "2": (" ### ", "#   #", "    #", "   # ", "  #  ", " #   ", "#####"),
    "3": ("#### ", "    #", "    #", " ### ", "    #", "    #", "#### "),
    "4": ("   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "),
    "5": ("#####", "#    ", "#### ", "    #", "    #", "#   #", " ### "),
    "6": (" ### ", "#    ", "#    ", "#### ", "#   #", "#   #", " ### "),
    "7": ("#####", "    #", "   # ", "   # ", "  #  ", "  #  ", "  #  "),
    "8": (" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "),
    "9": (" ### ", "#   #", "#   #", " ####", "    #", "    #", " ### "),
    ".": ("     ", "     ", "     ", "     ", "     ", " ##  ", " ##  "),
    ",": ("     ", "     ", "     ", "     ", " ##  ", " ##  ", " #   "),
    ":": ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", "     "),
    "'": ("  #  ", "  #  ", "  #  ", "     ", "     ", "     ", "     "),
    "-": ("     ", "     ", "     ", "#####", "     ", "     ", "     "),
    "!": ("  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "     ", "  #  "),
    "?": (" ### ", "#   #", "    #", "   # ", "  #  ", "     ", "  #  "),
    "%": ("##  #", "## # ", "   # ", "  #  ", " #   ", "# ## ", "#  ##"),
    "/": ("    #", "   # ", "   # ", "  #  ", " #   ", " #   ", "#    "),
    "(": ("   ##", "  #  ", " #   ", " #   ", " #   ", "  #  ", "   ##"),
    ")": ("##   ", "  #  ", "   # ", "   # ", "   # ", "  #  ", "##   "),
    "+": ("     ", "  #  ", "  #  ", "#####", "  #  ", "  #  ", "     "),
    " ": ("     ", "     ", "     ", "     ", "     ", "     ", "     "),
}


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def wrap_text(s, max_chars):
    """Greedy word wrap; returns a list of lines, each <= max_chars."""
    words = s.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = w if not cur else cur + " " + w
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------ canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        row = bytes(bg) * w
        self.rows = [bytearray(row) for _ in range(h)]

    def fill_rect(self, x, y, w, h, color):
        if w <= 0 or h <= 0:
            return
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x0 >= x1 or y0 >= y1:
            return
        chunk = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            self.rows[yy][x0 * 3:x1 * 3] = chunk

    def vgrad(self, x, y, w, h, top, bottom):
        if h <= 1:
            self.fill_rect(x, y, w, h, top)
            return
        for i in range(h):
            t = i / (h - 1)
            c = tuple(round(top[k] + (bottom[k] - top[k]) * t) for k in range(3))
            self.fill_rect(x, y + i, w, 1, c)

    def hline(self, x, y, w, color):
        self.fill_rect(x, y, w, 1, color)

    def vline(self, x, y, h, color):
        self.fill_rect(x, y, 1, h, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        half = thick // 2
        while True:
            self.fill_rect(x - half, y - half, thick, thick, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def polyline(self, pts, color, thick=1):
        for a, b in zip(pts, pts[1:]):
            self.line(a[0], a[1], b[0], b[1], color, thick)

    def circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def ring(self, cx, cy, r, color, thick=2):
        for k in range(thick):
            rr = r - k
            for dy in range(-rr, rr + 1):
                dx = int((rr * rr - dy * dy) ** 0.5)
                self.fill_rect(cx - dx, cy + dy, 1, 1, color)
                self.fill_rect(cx + dx, cy + dy, 1, 1, color)

    def triangle(self, x0, y0, x1, y1, x2, y2, color):
        ymin = max(0, min(y0, y1, y2))
        ymax = min(self.h - 1, max(y0, y1, y2))
        for yy in range(ymin, ymax + 1):
            xs = []
            for (ax, ay), (bx, by) in (((x0, y0), (x1, y1)),
                                       ((x1, y1), (x2, y2)),
                                       ((x2, y2), (x0, y0))):
                if ay == by:
                    continue
                if min(ay, by) <= yy <= max(ay, by):
                    t = (yy - ay) / (by - ay)
                    xs.append(ax + t * (bx - ax))
            if len(xs) >= 2:
                xa, xb = int(min(xs)), int(max(xs))
                self.fill_rect(xa, yy, xb - xa + 1, 1, color)

    def text(self, x, y, s, scale, color):
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for gy, row in enumerate(glyph):
                for gx, cell in enumerate(row):
                    if cell == "#":
                        self.fill_rect(cx + gx * scale, y + gy * scale,
                                       scale, scale, color)
            cx += 6 * scale
        return cx

    def text_block(self, x, y, lines, scale, color, spacing=4):
        yy = y
        for line in lines:
            self.text(x, yy, line, scale, color)
            yy += 7 * scale + spacing
        return yy

    def to_png(self):
        raw = b"".join(b"\x00" + bytes(row) for row in self.rows)
        comp = zlib.compress(raw, 6)

        def chunk(tag, data):
            c = struct.pack(">I", len(data)) + tag + data
            return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

        ihdr = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
                + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


# ------------------------------------------------------------------ scenes
def scene_gulf(c, x, y, w, h):
    """Dusk over the Gulf: sea, tanker, missile arcs, explosion."""
    c.vgrad(x, y, w, h, (31, 36, 64), (232, 130, 30))
    horizon = y + int(h * 0.68)
    c.vgrad(x, horizon, w, y + h - horizon, (14, 42, 74), (7, 26, 48))
    # low sun
    c.circle(x + int(w * 0.78), horizon - 18, 26, (255, 176, 32))
    c.circle(x + int(w * 0.78), horizon - 18, 18, (255, 214, 90))
    # stars in the upper sky (fixed positions)
    for sx, sy in ((40, 18), (120, 34), (210, 14), (330, 26), (470, 12),
                   (620, 30), (760, 16), (880, 30), (950, 14)):
        c.fill_rect(x + sx, y + sy, 3, 3, WHITE)
    # missile arcs with bright heads
    c.polyline([(x + 90, y + 8), (x + 190, y + 55), (x + 300, y + 118)],
               (255, 209, 102), 3)
    c.circle(x + 300, y + 118, 6, (255, 243, 176))
    c.polyline([(x + 560, y + 4), (x + 640, y + 60), (x + 700, y + 128)],
               (255, 209, 102), 3)
    c.circle(x + 700, y + 128, 6, (255, 243, 176))
    c.polyline([(x + 880, y + 10), (x + 830, y + 70), (x + 790, y + 132)],
               (255, 209, 102), 3)
    c.circle(x + 790, y + 132, 6, (255, 243, 176))
    # tanker silhouette on the sea
    ty = horizon + 26
    c.fill_rect(x + 330, ty, 330, 26, (10, 12, 18))
    c.fill_rect(x + 350, ty - 34, 150, 34, (16, 20, 30))
    c.fill_rect(x + 520, ty - 52, 26, 52, (16, 20, 30))
    c.fill_rect(x + 516, ty - 60, 34, 8, (200, 60, 40))
    for wx in range(360, 490, 22):
        c.fill_rect(x + wx, ty - 26, 10, 8, (255, 209, 102))
    # reflection streaks
    for rx in range(350, 640, 34):
        c.fill_rect(x + rx, ty + 30, 22, 3, (60, 110, 160))
    # explosion burst near the tanker
    ex, ey = x + 690, ty + 6
    c.circle(ex, ey, 26, (234, 88, 12))
    c.circle(ex, ey, 17, (250, 150, 40))
    c.circle(ex, ey, 9, (255, 214, 90))
    for dx, dy in ((-38, -14), (38, -18), (-30, 22), (34, 24), (0, -34)):
        c.line(ex, ey, ex + dx, ey + dy, (255, 176, 32), 3)
    # base / radar mast silhouette on the right shore
    bx = x + w - 110
    c.fill_rect(bx, horizon - 46, 60, 46, (8, 10, 16))
    c.fill_rect(bx + 28, horizon - 78, 4, 32, (8, 10, 16))
    c.circle(bx + 30, horizon - 80, 9, (8, 10, 16))
    c.circle(bx + 30, horizon - 82, 4, (255, 80, 80))


def scene_ukraine(c, x, y, w, h):
    """Night skyline under a missile barrage."""
    c.vgrad(x, y, w, h, (10, 25, 49), (27, 42, 74))
    for sx, sy in ((30, 12), (110, 26), (200, 10), (300, 22), (400, 14),
                   (460, 28)):
        c.fill_rect(x + sx, y + sy, 2, 2, WHITE)
    # missile streaks
    c.line(x + 60, y + 6, x + 130, y + 78, (255, 255, 255), 2)
    c.circle(x + 130, y + 78, 5, (255, 243, 176))
    c.line(x + 300, y + 2, x + 330, y + 66, (255, 255, 255), 2)
    c.circle(x + 330, y + 66, 5, (255, 243, 176))
    c.line(x + 430, y + 10, x + 400, y + 84, (255, 209, 102), 2)
    c.circle(x + 400, y + 84, 5, (255, 243, 176))
    # skyline
    base = y + h
    heights = [52, 78, 44, 92, 60, 84, 48, 70, 58, 88]
    bw = w // len(heights)
    for i, hh in enumerate(heights):
        bx = x + i * bw
        c.fill_rect(bx + 2, base - hh, bw - 4, hh, (5, 8, 14))
        for wy in range(base - hh + 8, base - 8, 14):
            for wx in range(bx + 8, bx + bw - 8, 12):
                if (wx + wy) % 3 == 0:
                    c.fill_rect(wx, wy, 3, 4, (255, 209, 102))
    # explosions over the city
    for ex, ey, r in ((x + 150, base - 96, 20), (x + 360, base - 108, 16)):
        c.circle(ex, ey, r, (234, 88, 12))
        c.circle(ex, ey, r - 7, (250, 150, 40))
        c.circle(ex, ey, r - 13, (255, 214, 90))
    # smoke puffs
    for sx, sy, r in ((x + 150, base - 122, 12), (x + 170, base - 128, 9),
                      (x + 360, base - 130, 10)):
        c.circle(sx, sy, r, (90, 96, 110))


def scene_cop31(c, x, y, w, h):
    """A globe pulled apart: oil pumpjack vs green leaf, COP31 deadlock."""
    c.vgrad(x, y, w, h, (220, 233, 245), (190, 210, 228))
    cx, cy, r = x + w // 2, y + h // 2 + 6, 52
    # globe
    c.circle(cx, cy, r, (30, 64, 175))
    c.circle(cx - 16, cy - 12, 16, (34, 139, 60))
    c.circle(cx + 18, cy + 8, 13, (34, 139, 60))
    c.circle(cx + 6, cy - 26, 10, (34, 139, 60))
    c.circle(cx - 24, cy + 20, 9, (46, 160, 80))
    # white cloud arcs
    c.fill_rect(cx - 30, cy - 34, 40, 4, WHITE)
    c.fill_rect(cx - 6, cy + 26, 34, 4, WHITE)
    # crack across the globe
    c.polyline([(cx - 34, cy - 40), (cx - 12, cy - 14), (cx + 4, cy + 6),
                (cx - 6, cy + 24), (cx + 20, cy + 44)], (20, 20, 20), 3)
    # oil pumpjack (left)
    px = x + 34
    c.fill_rect(px, y + h - 46, 54, 8, (30, 30, 30))
    c.fill_rect(px + 22, y + h - 96, 8, 50, (30, 30, 30))
    c.line(px + 26, y + h - 96, px + 66, y + h - 84, (30, 30, 30), 5)
    c.fill_rect(px + 62, y + h - 92, 12, 12, (30, 30, 30))
    c.line(px + 26, y + h - 96, px + 2, y + h - 70, (30, 30, 30), 4)
    # red X over the pumpjack
    c.line(px - 4, y + h - 108, px + 84, y + h - 44, RED, 4)
    c.line(px + 84, y + h - 108, px - 4, y + h - 44, RED, 4)
    # green sprout (right): stem with two small leaves
    lx, ly = x + w - 74, y + h - 78
    c.line(lx, ly + 22, lx, ly - 18, GREEN, 3)
    c.circle(lx - 12, ly - 8, 11, (34, 139, 60))
    c.circle(lx + 12, ly - 14, 11, (34, 139, 60))
    c.circle(lx, ly - 24, 9, (46, 160, 80))
    # tug arrows
    c.line(x + 96, cy, x + 128, cy, RED, 4)
    c.line(x + 128, cy, x + 116, cy - 7, RED, 4)
    c.line(x + 128, cy, x + 116, cy + 7, RED, 4)
    c.line(x + w - 96, cy, x + w - 128, cy, GREEN, 4)
    c.line(x + w - 128, cy, x + w - 116, cy - 7, GREEN, 4)
    c.line(x + w - 128, cy, x + w - 116, cy + 7, GREEN, 4)


def scene_markets(c, x, y, w, h):
    """A falling chart: red bars and a plunging line."""
    c.fill_rect(x, y, w, h, WHITE)
    # grid
    for gy in range(y + 16, y + h - 8, 22):
        c.hline(x + 8, gy, w - 16, (229, 229, 229))
    # descending bars
    bars = [58, 66, 60, 72, 64, 78, 70, 86, 80, 96]
    bw = (w - 40) // len(bars)
    base = y + h - 14
    for i, bh in enumerate(bars):
        bx = x + 20 + i * bw
        c.fill_rect(bx, base - bh, bw - 6, bh, (220, 60, 60))
    # plunging line with arrowhead (numbers live in the caption below)
    pts = [(x + 24, y + 22), (x + 80, y + 34), (x + 140, y + 30),
           (x + 200, y + 52), (x + 250, y + 48), (x + 300, y + 78)]
    c.polyline(pts, RED, 4)
    ex, ey = pts[-1]
    c.line(ex, ey, ex - 16, ey - 4, RED, 4)
    c.line(ex, ey, ex - 4, ey - 16, RED, 4)


def scene_mexico(c, x, y, w, h):
    """Night street: police car with flashing light bar, handcuffs."""
    c.vgrad(x, y, w, h, (16, 24, 40), (30, 41, 59))
    # road
    c.fill_rect(x, y + h - 34, w, 34, (12, 14, 18))
    c.fill_rect(x, y + h - 18, w, 2, (200, 200, 60))
    # police car silhouette, lightened so it reads against the night street
    cx, cy = x + 30, y + h - 78
    c.fill_rect(cx, cy + 22, 190, 22, (52, 64, 86))
    c.fill_rect(cx + 40, cy, 110, 24, (52, 64, 86))
    c.fill_rect(cx + 52, cy + 6, 34, 14, (180, 220, 250))
    c.fill_rect(cx + 100, cy + 6, 34, 14, (180, 220, 250))
    # light bar: red and blue flashers
    c.fill_rect(cx + 78, cy - 8, 16, 8, (220, 38, 38))
    c.fill_rect(cx + 96, cy - 8, 16, 8, (37, 99, 235))
    # wheels and headlights
    c.circle(cx + 40, cy + 44, 10, (0, 0, 0))
    c.circle(cx + 160, cy + 44, 10, (0, 0, 0))
    c.circle(cx + 216, cy + 30, 5, (255, 243, 176))
    # handcuffs (top right)
    hx, hy = x + w - 78, y + 34
    c.ring(hx, hy, 16, (201, 162, 39), 4)
    c.ring(hx + 42, hy + 10, 16, (201, 162, 39), 4)
    c.line(hx + 14, hy + 6, hx + 30, hy + 8, (201, 162, 39), 4)


def scene_peru(c, x, y, w, h):
    """Andes peaks, a crack, and a seismograph trace."""
    c.vgrad(x, y, w, h, (245, 230, 200), (220, 200, 160))
    base = y + h - 30
    # mountain range
    c.triangle(x + 6, base, x + 90, y + 26, x + 180, base, (75, 85, 99))
    c.triangle(x + 120, base, x + 210, y + 44, x + 300, base, (55, 65, 81))
    c.triangle(x + 230, base, x + 300, y + 18, x + 322, base, (75, 85, 99))
    # snowcaps
    c.triangle(x + 74, y + 44, x + 90, y + 26, x + 106, y + 44, WHITE)
    c.triangle(x + 196, y + 60, x + 210, y + 44, x + 224, y + 60, WHITE)
    c.triangle(x + 288, y + 36, x + 300, y + 18, x + 312, y + 36, WHITE)
    # crack down the middle peak (kept inside the scene, above the band)
    c.polyline([(x + 210, y + 44), (x + 198, y + 70), (x + 214, y + 88),
                (x + 200, y + 92)], (20, 20, 20), 3)
    # seismograph band
    c.fill_rect(x, base, w, 30, WHITE)
    c.polyline([(x + 6, base + 15), (x + 40, base + 15), (x + 52, base + 4),
                (x + 64, base + 26), (x + 76, base + 15), (x + 130, base + 15),
                (x + 142, base + 2), (x + 154, base + 28), (x + 166, base + 15),
                (x + 230, base + 15), (x + 242, base + 6), (x + 254, base + 24),
                (x + 266, base + 15), (x + 316, base + 15)], RED, 2)


# ------------------------------------------------------------------ panels
def panel(c, x, y, w, h, kicker, kcolor, headline, caption,
          scene=None, headline_scale=3, scene_frac=0.55):
    c.fill_rect(x, y, w, h, WHITE)
    c.fill_rect(x, y, w, 3, kcolor)
    inner = 14
    if scene is not None:
        sh = int(h * scene_frac)
        scene(c, x, y + 3, w, sh)
        ty = y + 3 + sh + 10
    else:
        ty = y + 12
    c.text(x + inner, ty, kicker, 2, kcolor)
    ty += 7 * 2 + 6
    max_chars = (w - 2 * inner) // (6 * headline_scale)
    lines = wrap_text(headline, max_chars)
    ty = c.text_block(x + inner, ty, lines, headline_scale, INK, spacing=3)
    ty += 2
    cap_chars = (w - 2 * inner) // 12
    cap_lines = wrap_text(caption, cap_chars)
    c.text_block(x + inner, ty, cap_lines, 2, DARKGREY, spacing=3)


def build():
    c = Canvas(W, H, PAPER)

    # ---------------------------------------------------------- masthead
    c.fill_rect(0, 0, W, 116, NAVY)
    c.text(24, 20, "THE WORLD TODAY", 6, WHITE)
    c.text(24, 76, "SIX STORIES THAT DEFINED THE DAY", 2, GOLD)
    date = "22 NOVEMBER 2026"
    c.text(W - 24 - text_width("SUNDAY", 2), 20, "SUNDAY", 2, GOLD)
    c.text(W - 24 - text_width(date, 4), 44, date, 4, WHITE)
    c.fill_rect(0, 110, W, 4, GOLD)

    # ------------------------------------------------------- lead: the Gulf
    lx, ly, lw, lh = 16, 128, 992, 330
    c.fill_rect(lx, ly, lw, lh, NAVY2)
    scene_gulf(c, lx, ly, lw, 212)
    band_y = ly + 212
    c.fill_rect(lx, band_y, lw, lh - 212, NAVY)
    c.fill_rect(lx, band_y, lw, 3, GOLD)
    c.text(lx + 24, band_y + 10, "THE GULF - LEAD STORY", 2, GOLD)
    c.text(lx + 24, band_y + 28, "GULF ON EDGE", 5, WHITE)
    c.text(lx + 24, band_y + 68,
           "IRAN HITS US BASES IN BAHRAIN", 3, WHITE)
    c.text(lx + 24, band_y + 94,
           "TANKERS HIT IN HORMUZ - TRUMP SEEKS A PERMANENT NUCLEAR DEAL",
           2, GOLD)

    # ------------------------------------------------------------ row two
    ry, rh = 470, 250
    panel(c, 16, ry, 490, rh, "UKRAINE - EUROPE", RED,
          "MISSILES RAIN ON UKRAINE",
          "400 DRONES AND 110 MISSILES IN ONE OF THE WAR'S BIGGEST "
          "BARRAGES. TWO KILLED IN KRYVYI RIH; MISSILES STRAY INTO POLAND.",
          scene=scene_ukraine)
    panel(c, 518, ry, 490, rh, "CLIMATE - COP31", GREEN,
          "CLIMATE TALKS IN DEADLOCK",
          "COP31 IN ANTALYA RUNS PAST ITS DEADLINE AS COUNTRIES SPLIT "
          "OVER FOSSIL FUELS.",
          scene=scene_cop31)

    # ---------------------------------------------------------- row three
    by, bh, bw = 732, 248, 325
    panel(c, 16, by, bw, bh, "MARKETS", RED,
          "AI SELL-OFF HITS MARKETS",
          "S&P 500 FALLS 3.7%. NIKKEI DOWN 5.1%.",
          scene=scene_markets, scene_frac=0.50)
    panel(c, 349, by, bw, bh, "MEXICO", DARKRED,
          "CARTEL BOSS CAPTURED",
          "'EL CHAPO ISIDRO' SEIZED; 11 KILLED IN SINALOA.",
          scene=scene_mexico, scene_frac=0.50)
    panel(c, 682, by, bw, bh, "PERU - DISASTER", BROWN,
          "6.9 QUAKE HITS PERU",
          "FELT IN LIMA. NO CASUALTIES REPORTED.",
          scene=scene_peru, scene_frac=0.50)

    # -------------------------------------------------------------- footer
    foot = ("SUNDAY 22 NOVEMBER 2026 - SOURCES: BBC, REUTERS, AP, "
            "EURONEWS, PBS, NPR")
    c.text((W - text_width(foot, 2)) // 2, 996, foot, 2, DARKGREY)
    return c


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    png = build().to_png()
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(png)
    print("wrote %s (%d bytes)" % (path, len(png)))


if __name__ == "__main__":
    main()
