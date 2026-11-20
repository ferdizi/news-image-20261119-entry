#!/usr/bin/env python3
"""Draw the v2 poster for news-image-20261119 (make.fun).

One square broadsheet, 1024x1024, summing up Thursday 19 November 2026:
35 verified stories (13 mains + 22 also-on), led by the first-ever
Trump-Xi-Putin trilateral summit in Shenzhen. Everything is drawn in code
with Pillow (shapes only, no photos): masthead, region bar, key-numbers
strip, RIGOR bar, three large lead panels, a 5x2 medium grid, a dotted
world map with numbered pins, also-on one-liners, a VERDICT box with a
UTC timeline, a DATE CHECK box and a sources footer.

Run:  python3 tools/render.py     (writes entry.png next to main.py)
The poster is deterministic: same bytes on every run, no network, no
timestamps, no metadata chunks. Fonts are bundled under fonts/.
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FONTS = os.path.join(ROOT, "fonts")
OUT = os.path.join(ROOT, "entry.png")

S = 2          # supersample factor: draw at 2048, downscale to 1024
W = 1024
H = 1024

# ---------------------------------------------------------------- palette
CREAM = (250, 248, 245)      # newsprint paper
PAPER2 = (244, 239, 230)     # slightly deeper cream for panels
INK = (24, 30, 62)           # dark navy text
INK_SOFT = (58, 62, 88)
RULE = (196, 30, 58)         # restrained red masthead rule
GOLD = (184, 138, 30)
TEAL = (14, 120, 118)        # world
VERMILION = (196, 30, 58)    # politics
OCHRE = (176, 118, 20)       # economy
VIOLET = (112, 66, 180)      # culture
GREEN = (28, 140, 74)        # sports
COBALT = (28, 82, 180)       # tech
GREY = (110, 112, 128)
CONF_GREEN = (28, 140, 74)
CLAIM_ORANGE = (214, 110, 20)
CARD_LINE = (214, 206, 192)

CAT_COLOR = {
    "WORLD": TEAL,
    "POLITICS": VERMILION,
    "ECONOMY": OCHRE,
    "CULTURE": VIOLET,
    "SPORTS": GREEN,
    "TECH": COBALT,
}

REGION_COLOR = {
    "ASIA": (176, 118, 20),
    "EUROPE": (28, 82, 180),
    "MIDDLE EAST": (14, 120, 118),
    "AFRICA": (28, 140, 74),
    "AMERICAS": (196, 30, 58),
    "OCEANIA": (112, 66, 180),
    "GLOBAL": (110, 112, 128),
}

# ---------------------------------------------------------------- fonts
def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size * S)

F_SERIF = lambda s: font("NotoSerif-Bold.ttf", s)      # noqa: E731
F_SERIF_R = lambda s: font("NotoSerif-Regular.ttf", s)  # noqa: E731
F_SANS = lambda s: font("Inter-Regular.otf", s)         # noqa: E731
F_SANS_B = lambda s: font("Inter-Bold.otf", s)          # noqa: E731
F_SANS_SB = lambda s: font("Inter-SemiBold.otf", s)     # noqa: E731
F_SANS_XB = lambda s: font("Inter-ExtraBold.otf", s)    # noqa: E731

# ---------------------------------------------------------------- data
# MAINS: (num, region, category, location, headline, deck, source,
#         status, lon, lat)
MAINS = [
    (1, "ASIA", "WORLD", "SHENZHEN",
     "Trump, Xi and Putin hold first-ever three-way summit",
     "First trilateral talks at APEC end with a joint \u201cDeclaration "
     "toward Peace\u201d; Ukraine is not mentioned.",
     "Times / NY Post", "CONFIRMED", 114.1, 22.5),
    (2, "ASIA", "WORLD", "THE HAGUE",
     "ICJ: Myanmar committed genocide against the Rohingya",
     "A 9\u20136 ruling \u2014 the first time a state is held responsible "
     "for genocide; reparations are ordered.",
     "WSJ / BBC", "CONFIRMED", 4.3, 52.1),
    (3, "GLOBAL", "WORLD", "ANTALYA",
     "COP31 draft drops all fossil-fuel mention",
     "The slimmed draft cuts the $120bn-a-year goal and 64 paragraphs; "
     "talks are due to close on Friday.",
     "Reuters", "CONFIRMED", 30.7, 36.9),
    (4, "AMERICAS", "ECONOMY", "NEW YORK",
     "Anthropic IPO raises $81.3bn, the largest ever",
     "Shares open at $111.50 and close up 17% on Nasdaq.",
     "WSJ / Reuters", "CONFIRMED", -74.0, 40.7),
    (5, "GLOBAL", "CULTURE", "AUCKLAND",
     "GTA VI goes on sale after a 13-year wait",
     "Launch starts at midnight in New Zealand; Metacritic: 99.",
     "Kotaku / People", "CONFIRMED", 174.8, -36.8),
    (6, "ASIA", "WORLD", "ODISHA, INDIA",
     "Cyclone Akvan: Odisha evacuates 80,000+",
     "A severe storm bears down on the Bay of Bengal coast.",
     "Hindu BusinessLine", "CONFIRMED", 85.8, 20.3),
    (7, "EUROPE", "WORLD", "KERCH STRAIT",
     "Kerch bridge hit a third time in a week",
     "Missiles hit the rail span; trains resume in the afternoon.",
     "Reuters / CNN", "CONFIRMED", 36.5, 45.3),
    (8, "MIDDLE EAST", "WORLD", "RIYADH",
     "Houthi missile hits Riyadh\u2019s PIF Tower",
     "A projectile hits the 80-storey tower; no injuries reported.",
     "WSJ / Reuters", "CONFIRMED", 46.7, 24.7),
    (9, "OCEANIA", "ECONOMY", "CANBERRA",
     "Australia jobless hits 4.9%, highest since 2021",
     "Employment falls 43,500; jobless rate at a five-year high.",
     "ABS / Reuters", "CONFIRMED", 149.1, -35.3),
    (10, "ASIA", "CULTURE", "SEOUL",
     "Korea\u2019s Suneung: 551,864 sit the CSAT",
     "A record share of repeat takers \u2014 the most in 23 years.",
     "Yonhap", "CONFIRMED", 127.0, 37.5),
    (11, "ASIA", "POLITICS", "JAKARTA",
     "Indonesia passes 18-year asset-seizure law",
     "Parliament approves seizing graft assets without conviction.",
     "Reuters / Antara", "CONFIRMED", 106.8, -6.2),
    (12, "EUROPE", "POLITICS", "COPENHAGEN",
     "Denmark\u2013Greenland Arctic pact passes 109\u20130",
     "Folketing ratifies the security deal; more US bases to follow.",
     "AP / Reuters", "CONFIRMED", 12.6, 55.7),
    (13, "AFRICA", "POLITICS", "MOGADISHU",
     "Somalia expels the UAE ambassador",
     "Mogadishu orders the envoy out in 72 hours over sovereignty.",
     "Reuters / AP", "CONFIRMED", 45.3, 2.0),
]

# ALSO: (num, region, one-liner, lon, lat) — lon/lat None = no map pin
ALSO = [
    (14, "AMERICAS", "Bogot\u00e1 \u2014 Colombia strikes against tax bill (Infobae)", -74.1, 4.7),
    (15, "AMERICAS", "New York \u2014 Dow \u22121,101, closes below 50,000 (WSJ)", -74.0, 40.7),
    (16, "GLOBAL", "Bitcoin below $62,000, lowest since July (CoinDesk)", None, None),
    (17, "AMERICAS", "Bentonville \u2014 Walmart Q3 beats, outlook up (Zacks)", -94.2, 36.4),
    (18, "ASIA", "Mumbai \u2014 Sensex +990; Bank Nifty hits record (PTI)", 72.9, 19.1),
    (19, "EUROPE", "Berlin \u2014 Coalition of the Willing meets (Reuters)", 13.4, 52.5),
    (20, "ASIA", "Seoul \u2014 Ex-PM Han\u2019s 15-year term quashed (Reuters)", 127.0, 37.5),
    (21, "EUROPE", "Belgrade \u2014 Lecturer \u010cupi\u0107 elected speaker (AP)", 20.5, 44.8),
    (22, "ASIA", "Tokyo \u2014 Japan\u2013India agree live-fire training (AP)", 139.7, 35.7),
    (23, "EUROPE", "London \u2014 Tribunal confirms Apple order (Reuters)", -0.1, 51.5),
    (24, "OCEANIA", "Queensland \u2014 Spitfire wreck found, 128 years on (AP)", 142.5, -10.7),
    (25, "ASIA", "Waziristan \u2014 22 militants killed [CLAIM] (ISPR)", 70.0, 32.5),
    (26, "OCEANIA", "Wellington \u2014 Nicholls 113* as NZ post 243/5 (Cricinfo)", 174.8, -41.3),
    (27, "AFRICA", "Johannesburg \u2014 SA go top of the WTC table (Reuters)", 28.0, -26.2),
    (28, "EUROPE", "Turin \u2014 Zverev, Shelton reach ATP semi-finals (ATP)", 7.7, 45.1),
    (29, "EUROPE", "London \u2014 Lyon beat Arsenal 2\u20130 in UWCL (UEFA)", -0.1, 51.5),
    (30, "AFRICA", "Nairobi \u2014 Jepchirchir gets 3-year EPO ban (Reuters)", 36.8, -1.3),
    (31, "ASIA", "Ulaanbaatar \u2014 Mongolia leader resigns, 96\u2013104 (AP)", 106.9, 47.9),
    (32, "MIDDLE EAST", "Gaza \u2014 Israeli raid past Yellow Line ends (Reuters)", 34.5, 31.5),
    (33, "AFRICA", "Kogi \u2014 15 victims freed [18 NOV] (News Central)", 6.7, 7.8),
    (34, "ASIA", "Yongbyon \u2014 IAEA flags N. Korea [18 NOV] (Reuters)", 126.0, 39.8),
    (35, "OCEANIA", "Suva \u2014 Fiji drought disaster [18 NOV] (Reuters)", 178.4, -18.1),
]

# Region bar: (region, count) — must sum to 35
REGION_BAR = [
    ("ASIA", 11),
    ("EUROPE", 7),
    ("MIDDLE EAST", 2),
    ("AFRICA", 4),
    ("AMERICAS", 4),
    ("OCEANIA", 4),
    ("GLOBAL", 3),
]

# Key-numbers strip: (big figure, tiny label)
NUMBERS = [
    ("3", "PRESIDENTS AT ONE TABLE"),
    ("9\u20136", "ICJ GENOCIDE VOTE"),
    ("$120bn", "COP31 GOAL CUT"),
    ("$81.3bn", "ANTHROPIC IPO"),
    ("109\u20130", "ARCTIC PACT VOTE"),
    ("551,864", "KOREA EXAM TAKERS"),
]

DATE_CHECK = (
    "DATE CHECK \u2014 Every story above happened, or was first reported, on "
    "Thursday 19 November 2026. Deliberately left out: UK inflation (ONS said "
    "it ROSE to 3.6% on 18 Nov, not fell); Van Gogh\u2019s $190.4m sale (18 Nov); "
    "Nature\u2019s \u201cmissing billion years\u201d (4 Nov); Pew on Muslims and "
    "Christians (18 Nov); Kyiv \u201c40% without heat\u201d (unconfirmed). "
    "The Kogi rescue, IAEA Yongbyon and Fiji drought were announced 18 Nov "
    "and are shown above with their date."
)

VERDICT = (
    "THE VERDICT \u2014 A day of firsts: the first three-way summit, the "
    "first state found guilty of genocide, and the biggest IPO ever \u2014 "
    "while the climate draft quietly gave up on fossil fuels."
)

# UTC timeline: (time, label) — only sourced or derived times
TIMELINE = [
    ("01:42", "Missile hits Riyadh\u2019s PIF Tower"),
    ("13:30", "Missiles hit Kyiv\u2019s Dnieper bridges"),
    ("17:00", "Anthropic starts trading on Nasdaq"),
    ("21:00", "Dow closes \u22121,101, below 50,000"),
]

SOURCES = (
    "Sources: Reuters, AP, AFP, BBC, Al Jazeera, UN News, Euronews, ABC, "
    "RNZ, Xinhua, Times, WSJ, CNN, Yonhap, Antara, IMD, AIU, ATP, UEFA, "
    "ESPNcricinfo \u2014 2026-11-19"
)

FOOTER_NOTE = (
    "Claims are attributed, not stated as fact. Pictures and map: original, "
    "drawn in code."
)


def rigor_counts():
    conf = sum(1 for m in MAINS if m[7] == "CONFIRMED")
    claim = sum(1 for m in MAINS if m[7] == "CLAIM")
    fore = sum(1 for m in MAINS if m[7] == "FORECAST")
    conf += sum(1 for a in ALSO if "[CLAIM]" not in a[2])
    claim += sum(1 for a in ALSO if "[CLAIM]" in a[2])
    return conf, claim, fore


# ---------------------------------------------------------------- helpers
def tw(d, text, fnt):
    """Text width in final (1024) units. textlength returns the width
    in the supersampled pixel space (fonts are loaded at 2x), so divide
    by S before using it to position text in 1024-space."""
    return d.textlength(text, font=fnt) / S


def wrap(d, text, fnt, max_w):
    """Greedy word wrap to lines that fit max_w (final 1024 units)."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=fnt) <= max_w * S:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def txt(d, x, y, s, fnt, fill, anchor="la"):
    d.text((x * S, y * S), s, font=fnt, fill=fill, anchor=anchor)


def rrect(d, x0, y0, x1, y1, fill=None, outline=None, width=1, radius=6):
    d.rounded_rectangle([x0 * S, y0 * S, x1 * S, y1 * S],
                        radius=radius * S, fill=fill,
                        outline=outline, width=width * S)


def hline(d, x0, x1, y, fill, width=1):
    d.line([x0 * S, y * S, x1 * S, y * S], fill=fill, width=width * S)


def vline(d, x, y0, y1, fill, width=1):
    d.line([x * S, y0 * S, x * S, y1 * S], fill=fill, width=width * S)

# ---------------------------------------------------------------- world map
# Rough landmass as (lon, lat, rx, ry) ellipses; dots on a 3-degree grid
# inside any ellipse are drawn. Good enough for a dotted atlas at 300 px.
LAND = [
    (-100, 48, 34, 14), (-95, 32, 20, 8), (-86, 20, 8, 6),
    (-152, 64, 12, 6), (-42, 73, 10, 6),
    (-60, -10, 14, 17), (-65, -30, 8, 12),
    (15, 52, 18, 10), (25, 62, 12, 6), (-5, 40, 8, 5),
    (15, 5, 18, 14), (25, -18, 12, 12), (40, 8, 8, 8),
    (90, 50, 45, 15), (110, 30, 20, 12), (78, 22, 10, 10),
    (105, 12, 8, 8), (135, 40, 15, 8), (45, 35, 12, 8),
    (134, -25, 14, 8), (120, -2, 15, 5), (142, -5, 8, 4),
    (175, -41, 4, 4),
]


def _on_land(lon, lat):
    for cl, ca, rx, ry in LAND:
        if ((lon - cl) / rx) ** 2 + ((lat - ca) / ry) ** 2 <= 1.0:
            return True
    return False


def map_xy(lon, lat, mx, my, mw, mh):
    """Equirectangular: lon -180..180 -> x, lat 75..-60 -> y."""
    x = mx + (lon + 180.0) / 360.0 * mw
    y = my + (75.0 - lat) / 135.0 * mh
    return x, y


def draw_map(d, mx, my, mw, mh):
    """Dotted world map with numbered pins for the 13 mains and small
    dots for also-on places that have a location."""
    # frame
    rrect(d, mx, my, mx + mw, my + mh, fill=PAPER2,
          outline=CARD_LINE, width=1, radius=4)
    txt(d, mx + 10, my + 6, "WHERE IT HAPPENED", F_SANS_XB(11),
        INK, anchor="la")
    # dots
    gx, gy = mx + 8, my + 26
    gw, gh = mw - 16, mh - 34
    lon, lat = -180.0, 75.0
    while lat >= -60.0:
        while lon <= 180.0:
            if _on_land(lon, lat):
                px, py = map_xy(lon, lat, gx, gy, gw, gh)
                r = 1.6
                d.ellipse([px * S - r * S, py * S - r * S,
                           px * S + r * S, py * S + r * S],
                          fill=(178, 172, 156))
            lon += 3.0
        lon = -180.0
        lat -= 3.0
    # also-on dots (small, region colour)
    for _n, region, _t, olon, olat in ALSO:
        if olon is None:
            continue
        px, py = map_xy(olon, olat, gx, gy, gw, gh)
        col = REGION_COLOR[region]
        r = 2.2
        d.ellipse([px * S - r * S, py * S - r * S,
                   px * S + r * S, py * S + r * S], fill=col)
    # main pins (numbered circles)
    for m in MAINS:
        n, _r, _c, _l, _h, _de, _s, _st, olon, olat = m
        px, py = map_xy(olon, olat, gx, gy, gw, gh)
        col = CAT_COLOR[m[2]]
        r = 8
        d.ellipse([px * S - r * S, py * S - r * S,
                   px * S + r * S, py * S + r * S],
                  fill=col, outline=(255, 255, 255), width=1 * S)
        txt(d, px, py - 0.5, str(n), F_SANS_XB(9), (255, 255, 255),
            anchor="mm")


# ---------------------------------------------------------------- lead art
def art_summit(d, x, y, w, h):
    """Shenzhen skyline, a long table, three chairs, three folders
    (US / CHINA / RUSSIA) and a central declaration sheet. No faces."""
    # sky
    d.rectangle([x * S, y * S, (x + w) * S, (y + h) * S],
                fill=(38, 54, 96))
    # skyline silhouettes
    sky = [(0, 52, 22, 78), (24, 40, 44, 78), (46, 58, 62, 78),
           (64, 34, 86, 78), (88, 48, 104, 78), (106, 60, 124, 78),
           (126, 42, 148, 78), (150, 56, 168, 78), (170, 38, 192, 78),
           (194, 52, 214, 78), (216, 46, 238, 78), (240, 58, 258, 78),
           (260, 44, 282, 78), (284, 56, 304, 78)]
    for bx0, by0, bx1, by1 in sky:
        d.rectangle([(x + bx0) * S, (y + by0) * S,
                     (x + bx1) * S, (y + by1) * S],
                    fill=(58, 74, 118))
        # lit windows
        for wy in range(by0 + 6, by1 - 4, 10):
            d.rectangle([(x + bx0 + 4) * S, (y + wy) * S,
                         (x + bx0 + 8) * S, (y + wy + 4) * S],
                        fill=(232, 196, 90))
    # table
    d.rectangle([x * S, (y + h - 26) * S, (x + w) * S, (y + h - 14) * S],
                fill=(120, 84, 44))
    d.rectangle([x * S, (y + h - 14) * S, (x + w) * S, (y + h) * S],
                fill=(90, 62, 32))
    # three chairs
    for cx in (28, 132, 236):
        d.rectangle([(x + cx) * S, (y + h - 46) * S,
                     (x + cx + 40) * S, (y + h - 26) * S],
                    fill=(24, 30, 62))
    # three folders
    folders = [(36, (196, 30, 58), "US"),
               (140, (28, 82, 180), "CHINA"),
               (244, (184, 138, 30), "RUSSIA")]
    for fx, col, lab in folders:
        d.rectangle([(x + fx) * S, (y + h - 62) * S,
                     (x + fx + 34) * S, (y + h - 46) * S], fill=col)
        txt(d, x + fx + 17, y + h - 54, lab, F_SANS_B(7),
            (255, 255, 255), anchor="mm")
    # declaration sheet in the middle
    d.rectangle([(x + 128) * S, (y + h - 78) * S,
                 (x + 176) * S, (y + h - 60) * S],
                fill=(250, 248, 245), outline=(24, 30, 62), width=1 * S)
    for ly in range(h - 74, h - 62, 4):
        d.line([(x + 133) * S, (y + ly) * S,
                (x + 171) * S, (y + ly) * S],
               fill=(120, 116, 104), width=1 * S)


def art_icj(d, x, y, w, h):
    """Courthouse columns, scales of justice, and the 9-6 vote."""
    d.rectangle([x * S, y * S, (x + w) * S, (y + h) * S],
                fill=(232, 228, 216))
    # pediment
    d.polygon([(x * S, (y + 22) * S),
               ((x + w // 2) * S, (y + 2) * S),
               ((x + w) * S, (y + 22) * S)], fill=(24, 30, 62))
    # four columns, leaving the centre open for the scales
    for cx in (24, 84, 216, 276):
        d.rectangle([(x + cx) * S, (y + 24) * S,
                     (x + cx + 16) * S, (y + h - 26) * S],
                    fill=(250, 248, 245), outline=(24, 30, 62),
                    width=1 * S)
    # scales of justice, centre
    cx, cy = x + w // 2, y + 32
    d.line([cx * S, cy * S, cx * S, (cy + 30) * S],
           fill=(184, 138, 30), width=2 * S)
    d.line([(cx - 26) * S, cy * S, (cx + 26) * S, cy * S],
           fill=(184, 138, 30), width=2 * S)
    for sx in (-26, 26):
        d.polygon([((cx + sx - 9) * S, (cy + 12) * S),
                   ((cx + sx + 9) * S, (cy + 12) * S),
                   ((cx + sx) * S, (cy + 22) * S)],
                  fill=(184, 138, 30))
        d.line([(cx + sx) * S, cy * S, (cx + sx) * S, (cy + 12) * S],
               fill=(184, 138, 30), width=1 * S)
    # vote badge below the scales
    d.rectangle([(x + w // 2 - 30) * S, (y + h - 20) * S,
                 (x + w // 2 + 30) * S, (y + h - 6) * S],
                fill=(24, 30, 62))
    txt(d, x + w // 2, y + h - 13, "9 \u2013 6", F_SERIF(12),
        (255, 255, 255), anchor="mm")


def art_cop(d, x, y, w, h):
    """A draft document: 'FOSSIL FUELS' struck through, $120bn cut."""
    d.rectangle([x * S, y * S, (x + w) * S, (y + h) * S],
                fill=(226, 238, 232))
    # document sheet
    d.rectangle([(x + 30) * S, (y + 6) * S,
                 (x + w - 30) * S, (y + h - 6) * S],
                fill=(250, 248, 245), outline=(24, 30, 62), width=1 * S)
    txt(d, x + w // 2, y + 16, "DRAFT \u2014 COP31", F_SANS_XB(11),
        INK, anchor="ma")
    for ly in range(30, 46, 6):
        d.line([(x + 44) * S, (y + ly) * S,
                (x + w - 44) * S, (y + ly) * S],
               fill=(178, 172, 156), width=1 * S)
    # struck-through fossil fuels
    txt(d, x + w // 2, y + 50, "FOSSIL FUELS", F_SANS_XB(15),
        (196, 30, 58), anchor="ma")
    d.line([(x + 52) * S, (y + 59) * S,
            (x + w - 52) * S, (y + 59) * S],
           fill=(196, 30, 58), width=2 * S)
    # downward arrow + cut figure
    ax = x + w // 2
    d.line([ax * S, (y + 64) * S, ax * S, (y + 72) * S],
           fill=(196, 30, 58), width=2 * S)
    d.polygon([(ax * S, (y + 77) * S),
               ((ax - 7) * S, (y + 68) * S),
               ((ax + 7) * S, (y + 68) * S)], fill=(196, 30, 58))
    txt(d, x + w // 2, y + h - 11, "$120bn CUT", F_SANS_XB(12),
        (196, 30, 58), anchor="ma")


LEAD_ART = {1: art_summit, 2: art_icj, 3: art_cop}


# ---------------------------------------------------------------- medium icons
def draw_icon(d, kind, x, y, size, col):
    """Small white glyph on a coloured rounded square."""
    rrect(d, x, y, x + size, y + size, fill=col, radius=5)
    cx, cy = x + size // 2, y + size // 2
    w = (255, 255, 255)
    if kind == "chart":          # bars
        for i, bh in enumerate((8, 13, 18)):
            bx = x + 6 + i * 8
            d.rectangle([bx * S, (cy + 10 - bh) * S,
                         (bx + 5) * S, (cy + 10) * S], fill=w)
    elif kind == "game":         # controller
        d.rounded_rectangle([(x + 5) * S, (cy - 6) * S,
                             (x + size - 5) * S, (cy + 6) * S],
                            radius=6 * S, fill=w)
        d.ellipse([(x + 8) * S, (cy - 2) * S, (x + 12) * S, (cy + 2) * S],
                  fill=col)
        d.ellipse([(x + size - 12) * S, (cy - 2) * S,
                   (x + size - 8) * S, (cy + 2) * S], fill=col)
    elif kind == "storm":        # cyclone swirl
        for r in (4, 8, 12):
            d.arc([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S],
                  start=20 + r * 8, end=200 + r * 8, fill=w, width=2 * S)
    elif kind == "bridge":       # arch bridge
        d.arc([(x + 4) * S, (cy - 4) * S, (x + size - 4) * S, (cy + 14) * S],
              start=180, end=360, fill=w, width=2 * S)
        d.line([(x + 4) * S, (cy + 8) * S, (x + size - 4) * S, (cy + 8) * S],
               fill=w, width=2 * S)
    elif kind == "tower":        # tall tower
        d.polygon([(cx * S, (y + 4) * S),
                   ((cx + 5) * S, (y + 10) * S),
                   ((cx - 5) * S, (y + 10) * S)], fill=w)
        d.rectangle([(cx - 6) * S, (y + 10) * S, (cx + 6) * S,
                     (y + size - 5) * S], fill=w)
    elif kind == "down":         # falling arrow
        d.line([(x + 6) * S, (cy - 8) * S, (x + size - 6) * S, (cy + 8) * S],
               fill=w, width=2 * S)
        d.line([(x + size - 12) * S, (cy + 8) * S,
                (x + size - 6) * S, (cy + 8) * S], fill=w, width=2 * S)
        d.line([(x + size - 6) * S, (cy + 2) * S,
                (x + size - 6) * S, (cy + 8) * S], fill=w, width=2 * S)
    elif kind == "exam":         # pencil
        d.line([(x + 7) * S, (y + size - 8) * S,
                (x + size - 8) * S, (y + 7) * S], fill=w, width=3 * S)
        d.polygon([((x + size - 8) * S, (y + 7) * S),
                   ((x + size - 4) * S, (y + 7) * S),
                   ((x + size - 8) * S, (y + 11) * S)], fill=w)
    elif kind == "gavel":        # gavel
        d.rectangle([(x + 7) * S, (cy - 8) * S, (x + size - 7) * S,
                     (cy - 3) * S], fill=w)
        d.line([(cx) * S, (cy - 3) * S, (cx + 8) * S, (cy + 9) * S],
               fill=w, width=2 * S)
        d.rectangle([(cx + 4) * S, (cy + 7) * S, (cx + 12) * S,
                     (cy + 11) * S], fill=w)
    elif kind == "snow":         # snowflake
        for ang in (0, 60, 120):
            import math as _m
            dx, dy = _m.cos(_m.radians(ang)), _m.sin(_m.radians(ang))
            d.line([cx * S, cy * S,
                    (cx + dx * 10) * S, (cy + dy * 10) * S],
                   fill=w, width=2 * S)
    elif kind == "flag":         # flag
        d.line([(x + 8) * S, (y + 5) * S, (x + 8) * S, (y + size - 5) * S],
               fill=w, width=2 * S)
        d.polygon([((x + 8) * S, (y + 5) * S),
                   ((x + size - 6) * S, (y + 9) * S),
                   ((x + 8) * S, (y + 13) * S)], fill=w)
    else:                        # generic dot
        d.ellipse([(cx - 5) * S, (cy - 5) * S, (cx + 5) * S, (cy + 5) * S],
                  fill=w)


MEDIUM_ICON = {
    4: "chart", 5: "game", 6: "storm", 7: "bridge", 8: "tower",
    9: "down", 10: "exam", 11: "gavel", 12: "snow", 13: "flag",
}

# ---------------------------------------------------------------- layout
MX = 28            # left margin
MW = 968           # content width
RIGHT = MX + MW


def draw_masthead(d):
    txt(d, MX, 16, "THE WORLD IN ONE DAY", F_SANS_XB(13), INK, anchor="la")
    txt(d, RIGHT, 16, "35 STORIES \u2014 EVERY CONTINENT",
        F_SANS_XB(13), INK, anchor="ra")
    txt(d, MX + MW // 2, 34, "Thursday 19 November 2026",
        F_SERIF(46), INK, anchor="ma")
    sub = ("Three presidents meet in Shenzhen \u00b7 ICJ finds Myanmar "
           "guilty of genocide \u00b7 COP31 draft drops fossil fuels")
    txt(d, MX + MW // 2, 88, sub, F_SANS(13), INK_SOFT, anchor="ma")
    hline(d, MX, RIGHT, 108, RULE, width=3)


def draw_region_bar(d, y):
    slot = MW / len(REGION_BAR)
    for i, (region, count) in enumerate(REGION_BAR):
        cx = MX + slot * i + slot / 2
        col = REGION_COLOR[region]
        label = f"{region} {count}"
        w = tw(d, label, F_SANS_B(12))
        dot_r = 4
        tx = cx - (w + dot_r * 2 + 5) / 2
        d.ellipse([(tx) * S, (y + 4) * S, (tx + dot_r * 2) * S,
                   (y + 4 + dot_r * 2) * S], fill=col)
        txt(d, tx + dot_r * 2 + 5, y + 1, label, F_SANS_B(12), INK,
            anchor="la")
    hline(d, MX, RIGHT, y + 20, CARD_LINE, width=1)


def draw_numbers(d, y):
    cell = MW / len(NUMBERS)
    for i, (fig, lab) in enumerate(NUMBERS):
        cx = MX + cell * i + cell / 2
        txt(d, cx, y, fig, F_SANS_XB(24), INK, anchor="ma")
        txt(d, cx, y + 26, lab, F_SANS_B(9), GREY, anchor="ma")
        if i:
            vline(d, MX + cell * i, y + 2, y + 38, CARD_LINE, width=1)
    hline(d, MX, RIGHT, y + 42, CARD_LINE, width=1)


def draw_rigor(d, y):
    conf, claim, fore = rigor_counts()
    total = conf + claim + fore
    label = (f"RIGOR \u2014 {conf} CONFIRMED \u00b7 {claim} CLAIM \u00b7 "
             f"{fore} FORECAST")
    txt(d, MX, y, label, F_SANS_B(11), INK, anchor="la")
    bx = MX + 268
    bw = RIGHT - bx
    bh = 12
    # segments proportional to counts
    x0 = bx
    for count, col in ((conf, CONF_GREEN), (claim, CLAIM_ORANGE),
                       (fore, GREY)):
        seg = bw * count / total if total else 0
        if seg > 0:
            d.rectangle([x0 * S, y * S, (x0 + seg) * S, (y + bh) * S],
                        fill=col)
        x0 += seg
    d.rectangle([bx * S, y * S, (bx + bw) * S, (y + bh) * S],
                outline=INK, width=1 * S)
    # legend
    lx = bx
    for name, col in (("CONFIRMED", CONF_GREEN), ("CLAIM", CLAIM_ORANGE),
                      ("FORECAST", GREY)):
        d.rectangle([lx * S, (y + 16) * S, (lx + 8) * S, (y + 24) * S],
                    fill=col)
        txt(d, lx + 12, y + 15, name, F_SANS_B(8), GREY, anchor="la")
        lx += 12 + tw(d, name, F_SANS_B(8)) + 16


def draw_lead(d, m, x, y, w, h):
    n, region, cat, loc, head, deck, src, status, _lo, _la = m
    col = CAT_COLOR[cat]
    rrect(d, x, y, x + w, y + h, fill=(255, 255, 255),
          outline=CARD_LINE, width=1, radius=4)
    # art band
    art_h = 92
    LEAD_ART[n](d, x + 1, y + 1, w - 2, art_h)
    # category bar
    d.rectangle([x * S, (y + art_h + 1) * S, (x + w) * S,
                 (y + art_h + 5) * S], fill=col)
    # number badge + location
    txt(d, x + 10, y + art_h + 12, str(n), F_SANS_XB(16), col, anchor="la")
    txt(d, x + 30, y + art_h + 15, f"{loc} \u00b7 {cat}",
        F_SANS_B(10), INK_SOFT, anchor="la")
    # headline (serif, up to 2 lines)
    lines = wrap(d, head, F_SERIF(19), w - 20)
    yy = y + art_h + 34
    for ln in lines[:2]:
        txt(d, x + 10, yy, ln, F_SERIF(19), INK, anchor="la")
        yy += 22
    # deck (up to 2 lines)
    dlines = wrap(d, deck, F_SANS(11), w - 20)
    yy = y + art_h + 80
    for ln in dlines[:2]:
        txt(d, x + 10, yy, ln, F_SANS(11), INK_SOFT, anchor="la")
        yy += 14
    # source + verification tag
    tag = "CONFIRMED" if status == "CONFIRMED" else "CLAIM"
    tcol = CONF_GREEN if status == "CONFIRMED" else CLAIM_ORANGE
    txt(d, x + 10, y + h - 16, src, F_SANS(10), GREY, anchor="la")
    tw_ = tw(d, tag, F_SANS_B(9))
    tx = x + w - 10 - tw_
    txt(d, tx, y + h - 16, tag, F_SANS_B(9), tcol, anchor="la")


def draw_medium(d, m, x, y, w, h):
    n, region, cat, loc, head, deck, src, status, _lo, _la = m
    col = CAT_COLOR[cat]
    rrect(d, x, y, x + w, y + h, fill=(255, 255, 255),
          outline=CARD_LINE, width=1, radius=4)
    # accent bar on top
    d.rectangle([x * S, y * S, (x + w) * S, (y + 4) * S], fill=col)
    # icon + number + location
    draw_icon(d, MEDIUM_ICON[n], x + 7, y + 8, 24, col)
    txt(d, x + 38, y + 8, str(n), F_SANS_XB(14), col, anchor="la")
    txt(d, x + 38, y + 24, f"{loc} \u00b7 {cat}", F_SANS_B(8), GREY,
        anchor="la")
    # headline (up to 2 lines)
    lines = wrap(d, head, F_SANS_B(13), w - 14)
    yy = y + 36
    for ln in lines[:2]:
        txt(d, x + 7, yy, ln, F_SANS_B(13), INK, anchor="la")
        yy += 14
    # deck (up to 2 lines)
    dlines = wrap(d, deck, F_SANS(10.5), w - 14)
    yy = y + 66
    for ln in dlines[:2]:
        txt(d, x + 7, yy, ln, F_SANS(10.5), INK_SOFT, anchor="la")
        yy += 12
    # source + tag
    tag = "CONFIRMED" if status == "CONFIRMED" else "CLAIM"
    tcol = CONF_GREEN if status == "CONFIRMED" else CLAIM_ORANGE
    txt(d, x + 7, y + h - 12, src, F_SANS(9), GREY, anchor="la")
    tw_ = tw(d, tag, F_SANS_B(8))
    txt(d, x + w - 7 - tw_, y + h - 12, tag, F_SANS_B(8), tcol,
        anchor="la")

# ---------------------------------------------------------------- lower band
def draw_also(d, x, y, w, col_items):
    """One column of also-on one-liners: number + complete line."""
    yy = y
    for n, _region, text, _lon, _lat in col_items:
        num = f"{n}."
        nw = tw(d, num, F_SANS_B(11))
        txt(d, x, yy, num, F_SANS_B(11), INK, anchor="la")
        txt(d, x + nw + 5, yy, text, F_SANS(11), INK_SOFT, anchor="la")
        yy += 17
    return yy


def draw_lower(d, y):
    map_w, map_h = 330, 204
    draw_map(d, MX, y, map_w, map_h)
    ax = MX + map_w + 12
    aw = RIGHT - ax
    txt(d, ax, y, "ALSO ON THURSDAY 19 NOVEMBER 2026",
        F_SANS_XB(12), INK, anchor="la")
    col_w = (aw - 12) // 2
    half = (len(ALSO) + 1) // 2
    draw_also(d, ax, y + 20, col_w, ALSO[:half])
    draw_also(d, ax + col_w + 12, y + 20, col_w, ALSO[half:])


def draw_verdict_timeline(d, y):
    lines = wrap(d, VERDICT, F_SANS_B(12), MW)
    yy = y
    for ln in lines[:2]:
        txt(d, MX, yy, ln, F_SANS_B(12), INK, anchor="la")
        yy += 15
    # timeline: one line, bold times
    parts = ["19 NOV (UTC)"]
    for t, lab in TIMELINE:
        parts.append(f"{t} {lab}")
    line = "  \u00b7  ".join(parts)
    txt(d, MX, yy + 4, line, F_SANS(10), INK_SOFT, anchor="la")
    return yy + 4 + 13


def draw_datecheck(d, y):
    rrect(d, MX, y, RIGHT, y + 40, fill=PAPER2, outline=CARD_LINE,
          width=1, radius=4)
    lines = wrap(d, DATE_CHECK, F_SANS(9.5), MW - 20)
    yy = y + 5
    for ln in lines[:3]:
        txt(d, MX + 10, yy, ln, F_SANS(9.5), INK_SOFT, anchor="la")
        yy += 12


def draw_footer(d, y):
    txt(d, MX, y, FOOTER_NOTE, F_SANS(10), GREY, anchor="la")
    txt(d, MX, y + 13, SOURCES, F_SANS(10), GREY, anchor="la")


# ---------------------------------------------------------------- build
def draw():
    img = Image.new("RGB", (W * S, H * S), CREAM)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_region_bar(d, 116)
    draw_numbers(d, 142)
    draw_rigor(d, 190)
    # three lead cards
    lead_w = (MW - 16) // 3
    lead_y, lead_h = 222, 218
    for i, m in enumerate(MAINS[:3]):
        draw_lead(d, m, MX + i * (lead_w + 8), lead_y, lead_w, lead_h)
    # ten medium cards, 5x2
    med_w = (MW - 32) // 5
    med_h = 106
    med_y = 448
    for i, m in enumerate(MAINS[3:]):
        row, col = divmod(i, 5)
        draw_medium(d, m, MX + col * (med_w + 8),
                    med_y + row * (med_h + 8), med_w, med_h)
    draw_lower(d, 676)
    draw_verdict_timeline(d, 888)
    draw_datecheck(d, 940)
    draw_footer(d, 986)
    img = img.resize((W, H), Image.LANCZOS)
    img.save(OUT, "PNG")
    print(f"wrote {OUT} ({os.path.getsize(OUT)} bytes)")


if __name__ == "__main__":
    draw()
