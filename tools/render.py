#!/usr/bin/env python3
"""Thursday 19 November 2026 — one front page, 40 stories, 13 mains.

"The Day, Cross-Examined": a warm-ivory newspaper broadside. Giant serif
masthead, a day-in-numbers strip, a RIGOR BAR (verification counts for all
40 stories), three lead panels with flat PIL scene art, ten small mains in
a 5x2 grid, a dotted world map with numbered pins beside 27 also-on
one-liners, a one-sentence VERDICT beside a UTC timeline rail, and a
DATE CHECK footer naming the stories deliberately left out because they
were first reported before 19 November.

Every story is a real event from Thursday 19 November 2026, or first
reported that day (see FACTS.md in the study dir). Zero wrong-date mains:
the 18-November announcements (IAEA Yongbyon, Fiji drought, Kogi rescue)
sit in also-on only, with their date shown. Disputed or single-source
claims are flagged (the Pakistan raid is marked CLAIM). Number traps
avoided: Korea CSAT is 551,864 (not 491,000); the Sensex did not hit a
record (Bank Nifty and the BSE market cap did); Kyiv "40% without heat"
is unconfirmed and is not used; the Anthropic $83 pricing was 18 Nov, so
the story is framed as the trading debut.

Draws a 1024x1024 page with Pillow, supersampled 2x (rendered at 2048,
downscaled with Lanczos). Deterministic: same bytes on every run.
Run: python3 tools/render.py   (writes entry.png next to this repo root)
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

S = 2  # supersample factor; all layout numbers are in final (1024) units
W, H = 1024, 1024

PAPER = (250, 246, 238)      # warm ivory
INK = (26, 26, 26)           # near-black
RED = (176, 58, 46)          # restrained red (masthead rule, accents)
GOLD = (178, 140, 40)
NAVY = (24, 48, 92)
MUTED = (110, 104, 92)
PANEL_LINE = (210, 203, 188)
MAP_FILL = (238, 233, 220)
MAP_EDGE = (168, 159, 136)
MAP_DOT = (178, 169, 148)

# One accent per category, used only for rules, pins and labels.
CAT_COLOUR = {
    "WORLD": (0, 128, 128),       # teal
    "POLITICS": (198, 60, 40),    # vermilion
    "ECONOMY": (178, 140, 40),    # ochre
    "CULTURE": (110, 70, 160),    # violet
    "SPORTS": (40, 140, 70),      # green
    "TECH": (40, 80, 180),        # cobalt
}
REGION_COLOUR = {
    "ASIA": (46, 125, 50),
    "MIDDLE EAST": (176, 58, 46),
    "EUROPE": (31, 78, 121),
    "AFRICA": (20, 143, 119),
    "AMERICAS": (125, 60, 152),
    "OCEANIA": (202, 111, 30),
    "WORLD": (90, 90, 90),
}
# Verification-status colours for the RIGOR BAR and tags.
CONFIRMED_COL = (40, 140, 70)
CLAIM_COL = (202, 111, 30)
FORECAST_COL = (120, 120, 120)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FONTS = os.path.join(ROOT, "fonts")

SERIF_B = os.path.join(FONTS, "NotoSerif-Bold.ttf")
SERIF = os.path.join(FONTS, "NotoSerif-Regular.ttf")
SANS = os.path.join(FONTS, "Inter-Regular.otf")
SANS_M = os.path.join(FONTS, "Inter-Medium.otf")
SANS_SB = os.path.join(FONTS, "Inter-SemiBold.otf")
SANS_B = os.path.join(FONTS, "Inter-Bold.otf")
SANS_XB = os.path.join(FONTS, "Inter-ExtraBold.otf")


def F(path, size):
    """Load a bundled font at logical size (supersampled internally)."""
    return ImageFont.truetype(path, size * S)


def xy(x, y):
    return (x * S, y * S)


def box(x0, y0, x1, y1):
    return [x0 * S, y0 * S, x1 * S, y1 * S]


def pts(*coords):
    return [(x * S, y * S) for x, y in coords]


def font(path, size):
    return F(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns the lines that fit max_w (logical units)."""
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_w * S:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def balance_two(draw, text, fnt, max_w):
    """Split into the two most even lines that both fit max_w, else None."""
    words = text.split()
    best = None
    for k in range(1, len(words)):
        l1, l2 = " ".join(words[:k]), " ".join(words[k:])
        w1 = draw.textlength(l1, font=fnt)
        w2 = draw.textlength(l2, font=fnt)
        if w1 <= max_w * S and w2 <= max_w * S:
            score = max(w1, w2)
            if best is None or score < best[0]:
                best = (score, [l1, l2])
    return best[1] if best is not None else None


def fit_lines(draw, text, fnt, max_w, max_lines):
    """Wrap and cap to max_lines, adding an ellipsis when clipped."""
    lines = wrap(draw, text, fnt, max_w)
    if len(lines) <= max_lines:
        return lines
    out = lines[:max_lines]
    while out and draw.textlength(out[-1] + "\u2026", font=fnt) > max_w * S:
        out[-1] = out[-1][:-1]
    out[-1] = out[-1] + "\u2026"
    return out


def text_block(draw, x, y, lines, fnt, fill, leading):
    for i, line in enumerate(lines):
        draw.text(xy(x, y + i * leading), line, font=fnt, fill=fill)
    return y + len(lines) * leading


def badge(draw, cx, cy, n, colour, r=11):
    draw.ellipse(box(cx - r, cy - r, cx + r, cy + r), fill=colour,
                 outline=(255, 255, 255), width=2 * S)
    fnt = F(SANS_B, 11 if n < 10 else 10)
    tw = draw.textlength(str(n), font=fnt)
    th = fnt.getbbox(str(n))[3] - fnt.getbbox(str(n))[1]
    draw.text(xy(cx - tw / S / 2, cy - th / S / 2 - 1), str(n), font=fnt,
              fill=(255, 255, 255))


def sky(draw, x, y, w, h, top, bottom):
    """Vertical two-stop sky gradient, drawn as horizontal bands."""
    for row in range(h * S):
        t = row / max(h * S - 1, 1)
        col = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        draw.line([(x * S, y * S + row), ((x + w) * S, y * S + row)], fill=col)


def centred(draw, cx, y, text, fnt, fill):
    tw = draw.textlength(text, font=fnt)
    draw.text(xy(cx - tw / S / 2, y), text, font=fnt, fill=fill)


def _lcg(seed):
    """Deterministic tiny PRNG (LCG) — same sequence on every run."""
    s = seed
    while True:
        s = (1103515245 * s + 12345) & 0x7FFFFFFF
        yield s / 0x7FFFFFFF


def _dots(draw, x, y, w, h, col, step, r, seed, fill=0.62):
    """Deterministic dot texture over a region (windows, stars, grain)."""
    rng = _lcg(seed)
    row = 0
    yy = y + step // 2
    while yy < y + h:
        xx = x + step // 2 + (row % 2) * (step // 2)
        while xx < x + w:
            if next(rng) < fill:
                draw.ellipse(box(xx - r, yy - r, xx + r, yy + r), fill=col)
            xx += step
        yy += step
        row += 1


def _stars(draw, x, y, w, h, n, seed, col=(255, 255, 255)):
    """Deterministic scattered stars."""
    rng = _lcg(seed)
    for _ in range(n):
        sx = x + int(next(rng) * w)
        sy = y + int(next(rng) * h)
        r = 1 if next(rng) < 0.7 else 2
        draw.ellipse(box(sx - r, sy - r, sx + r, sy + r), fill=col)


def _burst(draw, cx, cy, r, col, spikes=8):
    """Starburst (impact flash) centred on cx, cy."""
    pts_list = []
    for i in range(spikes * 2):
        ang = math.pi * i / spikes
        rr = r if i % 2 == 0 else r * 0.45
        pts_list.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    draw.polygon(pts(*pts_list), fill=col)


# ------------------------------------------------------------------- map
# Rough continent outlines in lon/lat, drawn equirectangular.
LAND = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 70),
     (-75, 62), (-65, 60), (-55, 52), (-60, 47), (-70, 42), (-75, 35),
     (-80, 25), (-85, 20), (-90, 15), (-95, 18), (-105, 20), (-115, 28),
     (-125, 40), (-125, 48), (-140, 60), (-155, 58), (-165, 60)],
    [(-80, 10), (-75, 5), (-70, 0), (-65, -5), (-60, -10), (-55, -20),
     (-50, -30), (-45, -25), (-40, -20), (-35, -8), (-40, 0), (-50, 0),
     (-60, 5), (-70, 10), (-78, 8)],
    [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31), (35, 28),
     (40, 20), (43, 12), (48, 11), (51, 10), (45, 0), (40, -10), (35, -20),
     (30, -30), (20, -35), (15, -30), (12, -18), (13, -10), (9, 0), (0, 5),
     (-8, 5), (-13, 8)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 59), (28, 60), (30, 70), (25, 71), (18, 69),
     (12, 65), (5, 60), (0, 55), (-5, 50), (-10, 44)],
    [(30, 70), (40, 68), (55, 70), (70, 72), (90, 75), (110, 76), (130, 72),
     (150, 70), (160, 65), (162, 60), (158, 52), (142, 50), (140, 40),
     (130, 33), (127, 35), (122, 30), (115, 22), (108, 12), (105, 8),
     (100, 8), (95, 15), (90, 22), (85, 20), (80, 10), (75, 8), (70, 20),
     (65, 25), (60, 25), (55, 26), (50, 29), (48, 30), (43, 35), (40, 36),
     (35, 36), (30, 41)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (125, -32), (130, -32),
     (135, -35), (140, -38), (145, -38), (150, -37), (153, -32), (153, -27),
     (150, -22), (146, -19), (142, -11), (137, -12), (135, -15), (132, -12),
     (130, -13), (126, -14), (122, -17), (118, -20)],
]


def project(lon, lat, mx, my, mw, mh):
    px = mx + (lon + 180.0) / 360.0 * mw
    py = my + (85.0 - lat) / 145.0 * mh
    return px, py


def _inside(px, py, poly):
    """Ray-casting point-in-polygon for lon/lat polygons."""
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > py) != (y2 > py):
            xint = (py - y1) * (x2 - x1) / (y2 - y1) + x1
            if px < xint:
                inside = not inside
    return inside


def draw_map(draw, mx, my, mw, mh):
    draw.rectangle(box(mx, my, mx + mw, my + mh), fill=MAP_FILL,
                   outline=PANEL_LINE, width=S)
    inner = (mx + 4, my + 4, mw - 8, mh - 8)
    step_lon, step_lat = 4.0, 3.0
    lon = -180.0 + step_lon / 2
    while lon < 180.0:
        lat = -60.0 + step_lat / 2
        while lat < 85.0:
            if any(_inside(lon, lat, poly) for poly in LAND):
                px, py = project(lon, lat, *inner)
                draw.ellipse(box(px - 1.6, py - 1.6, px + 1.6, py + 1.6),
                             fill=MAP_DOT)
            lat += step_lat
        lon += step_lon
    for n, _region, _t, lon, lat in ALSO:
        if lon is None:
            continue
        px, py = project(lon, lat, *inner)
        draw.ellipse(box(px - 3, py - 3, px + 3, py + 3), fill=(120, 115, 105))
    for n, _region, _cat, _tag, _h, _d, _src, _st, lon, lat in MAINS:
        if lon is None:
            continue
        px, py = project(lon, lat, *inner)
        col = REGION_COLOUR[_region]
        draw.ellipse(box(px - 8, py - 8, px + 8, py + 8), fill=col,
                     outline=(255, 255, 255), width=2 * S)
        fnt = F(SANS_B, 8)
        tw = draw.textlength(str(n), font=fnt)
        draw.text(xy(px - tw / S / 2, py - 5), str(n), font=fnt,
                  fill=(255, 255, 255))

# ------------------------------------------------------------------- data
# MAINS: (n, region, category, tag, headline, deck, source, status, lon, lat)
# status: CONFIRMED (named sources) or CLAIM (single-source, flagged).
MAINS = [
    (1, "ASIA", "WORLD", "APEC SUMMIT",
     "TRUMP, XI AND PUTIN MEET FOR THE FIRST TIME",
     "First three-way talks in Shenzhen; a joint \u201cDeclaration "
     "toward Peace.\u201d",
     "TIMES / NY POST", "CONFIRMED", 114.1, 22.5),
    (2, "EUROPE", "WORLD", "ICJ RULING",
     "MYANMAR COMMITTED GENOCIDE, ICJ RULES 9\u20136",
     "First time a state is held responsible for genocide; reparations "
     "ordered, including safe return.",
     "WSJ / CNN / BBC", "CONFIRMED", 4.3, 52.1),
    (3, "EUROPE", "WORLD", "COP31",
     "COP31 DRAFT DROPS ALL FOSSIL-FUEL MENTION",
     "Slimmed from 144 to 80 paragraphs; the $120bn-a-year adaptation "
     "goal is cut.",
     "REUTERS", "CONFIRMED", 30.7, 36.9),
    (4, "AMERICAS", "ECONOMY", "IPO",
     "ANTHROPIC DEBUTS, BIGGEST IPO EVER",
     "980m shares at $83; opened $111.50, closed $97.17, up 17%.",
     "WSJ / REUTERS", "CONFIRMED", -74.0, 40.7),
    (5, "WORLD", "CULTURE", "GAMES",
     "GTA VI GOES ON SALE AFTER A 13-YEAR WAIT",
     "Midnight launch, New Zealand first; Metacritic 99 from 147 reviews.",
     "KOTAKU", "CONFIRMED", 174.8, -41.3),
    (6, "ASIA", "WORLD", "CYCLONE",
     "ODISHA EVACUATES 80,000+ FOR AKVAN",
     "Landfall due Fri 20 Nov; red alert in 6 districts, 69 trains cut.",
     "IMD / HBL", "CONFIRMED", 85.8, 20.3),
    (7, "EUROPE", "WORLD", "UKRAINE WAR",
     "KERCH BRIDGE HIT A THIRD TIME IN A WEEK",
     "Neptune missiles halt rail; the road has been impassable since Tuesday.",
     "REUTERS / CNN", "CONFIRMED", 36.5, 45.3),
    (8, "MIDDLE EAST", "WORLD", "RIYADH",
     "HOUTHI MISSILE HITS RIYADH\u2019S PIF TOWER",
     "Windows blown out across 7\u20138 floors; no injuries reported.",
     "WSJ / REUTERS", "CONFIRMED", 46.7, 24.7),
    (9, "AMERICAS", "WORLD", "COLOMBIA",
     "COLOMBIA STRIKES AGAINST TAX BILL",
     "Marches in five cities; 217,744 riders hit by 3pm.",
     "COLOMBIA REPORTS", "CONFIRMED", -74.1, 4.7),
    (10, "OCEANIA", "ECONOMY", "JOBS",
     "AUSTRALIA JOBLESS HITS 4.9%",
     "Employment fell 43,500; worst since Oct 2021.",
     "ABS / REUTERS", "CONFIRMED", 149.1, -35.3),
    (11, "ASIA", "CULTURE", "EXAM",
     "551,864 SIT KOREA\u2019S BIGGEST EXAM",
     "Repeat takers most in 23 years; 75,000 proctors on duty.",
     "YONHAP", "CONFIRMED", 127.0, 37.5),
    (12, "ASIA", "POLITICS", "LAW",
     "INDONESIA PASSES ASSET-SEIZURE LAW",
     "Ends an 18-year wait; seizure without conviction in some cases.",
     "REUTERS / ANTARA", "CONFIRMED", 106.8, -6.2),
    (13, "EUROPE", "POLITICS", "BERLIN",
     "BERLIN HOSTS UKRAINE COALITION",
     "30\u201340 leaders; \u20ac45bn EU support for Ukraine in 2027.",
     "REUTERS", "CONFIRMED", 13.4, 52.5),
]

# ALSO: (n, region, one-liner, lon, lat) — complete sentences, kept short
# enough to fit one line in the also-on columns (checked by verify).
# [18 Nov] = announced 18 Nov, reported 19 Nov. [CLAIM] = single source.
ALSO = [
    (14, "EUROPE", "Copenhagen: Arctic pact passes 109\u20130", 12.6, 55.7),
    (15, "AFRICA", "Nairobi: Jepchirchir banned 3 years for EPO", 36.8, -1.3),
    (16, "ASIA", "Ulaanbaatar: Mongolia accepts president\u2019s exit", 106.9, 47.9),
    (17, "MIDDLE EAST", "Gaza: raid past Yellow Line ends", 34.4, 31.4),
    (18, "AMERICAS", "Florida: floods shut schools, 15.3 in rain", -81.0, 26.0),
    (19, "EUROPE", "Paris: M\u00e9lenchon sees left coalition possible", 2.3, 48.9),
    (20, "ASIA", "Shenzhen: APEC adopts Leaders\u2019 Declaration", 114.1, 22.5),
    (21, "AMERICAS", "New York: Dow falls 1,101, below 50,000", -74.0, 40.7),
    (22, "WORLD", "Bitcoin drops below $62,000", None, None),
    (23, "EUROPE", "Kyiv: Russian missiles hit Dnieper bridges", 30.5, 50.4),
    (24, "AFRICA", "Kogi: police rescue 15 kidnap victims [18 Nov]", 7.5, 7.8),
    (25, "AMERICAS", "Bentonville: Walmart beats, raises guidance", -94.2, 36.4),
    (26, "ASIA", "Mumbai: Sensex jumps 990, Nifty tops 25,500", 72.9, 19.1),
    (27, "AFRICA", "Mogadishu: Somalia expels UAE ambassador", 45.3, 2.0),
    (28, "ASIA", "Seoul: court overturns ex-PM Han\u2019s sentence", 127.0, 37.5),
    (29, "EUROPE", "Belgrade: student lecturer elected speaker", 20.5, 44.8),
    (30, "ASIA", "Tokyo: Japan\u2013India agree first live-fire drills", 139.7, 35.7),
    (31, "EUROPE", "London: tribunal confirms Apple secrecy order", -0.1, 51.5),
    (32, "ASIA", "IAEA: N. Korea expands Yongbyon plant [18 Nov]", 126.0, 39.0),
    (33, "OCEANIA", "Suva: Fiji declares drought disaster [18 Nov]", 178.4, -17.7),
    (34, "OCEANIA", "Sydney: Spitfire wreck found, 128 years on", 151.2, -33.9),
    (35, "ASIA", "Peshawar: 22 militants killed in raids [CLAIM]", 71.6, 34.0),
    (36, "OCEANIA", "Wellington: Nicholls 113*, NZ 243/5 vs India", 174.8, -41.3),
    (37, "AFRICA", "Johannesburg: S. Africa top of WTC table", 28.0, -26.2),
    (38, "EUROPE", "Turin: Shelton, Zverev reach ATP semi-finals", 7.7, 45.1),
    (39, "EUROPE", "London: Lyon Women beat Arsenal 2\u20130", -0.1, 51.5),
    (40, "EUROPE", "Barcelona hit Servette 6\u20130, top of UWCL", 2.2, 41.4),
]

# The day in numbers (strip under the masthead): only verified 19-Nov figures.
NUMBERS = [
    ("9\u20136", "ICJ vote"),
    ("$120bn", "COP31 goal cut"),
    ("$81.3bn", "Anthropic IPO"),
    ("109\u20130", "Arctic vote"),
    ("4.9%", "Australia jobless"),
    ("551,864", "Korea exam"),
    ("13 yrs", "GTA V \u2192 VI"),
]

# Region counts across all 40 stories (for the bar in the footer).
REGION_BAR = [("ASIA", 12), ("EUROPE", 10), ("AMERICAS", 5), ("AFRICA", 4),
              ("OCEANIA", 4), ("WORLD", 3), ("MIDDLE EAST", 2)]

# RIGOR counts are computed from the data: 39 CONFIRMED mains+briefs,
# 1 CLAIM (the Pakistan raid, single military source), 0 FORECAST.
RIGOR_NOTE = ("every main verified against a named source; "
              "the single-source claim is flagged [CLAIM] in the briefs")

DATE_CHECK = ("Left out on purpose \u2014 first reported before 19 November: "
              "Van Gogh $190.4m sale (18 Nov) \u00b7 Nature \u2018missing billion "
              "years\u2019 (4 Nov) \u00b7 Pew Muslims/Christians (18 Nov) \u00b7 UK "
              "inflation \u2018falls\u2019 \u2014 wrong, CPI rose to 3.6% (18 Nov) "
              "\u00b7 Nvidia results \u00b7 Voyager 1 one light-day \u00b7 EU "
              "\u20ac45bn Ukraine loan \u00b7 Jeffries 251\u201311 \u00b7 COP31 first "
              "draft \u00b7 An-12 crash \u00b7 Japan stimulus \u00b7 Goldman India "
              "upgrade (18 Nov) \u00b7 ICE contempt ruling (18 Nov).")

SOURCES = ("Sources: Reuters, AP, AFP, BBC, WSJ, CNN, Al Jazeera, Xinhua, "
           "Yonhap, ABS, IMD, ICJ, ATP, UEFA, ESPNcricinfo \u2014 every story "
           "happened, or was first reported, on Thursday 19 November 2026. "
           "Original drawings.")

VERDICT = ("Three presidents talked peace in Shenzhen, a court ruled "
           "genocide, and the climate draft lost its teeth.")

# UTC timeline rail: only sourced times. (Riyadh 04:42 local = 01:42 UTC;
# Kyiv bridges 13:30 UTC; Anthropic midday ET \u2248 17:00 UTC; Dow close
# 16:00 ET = 21:00 UTC.)
TIMELINE = [
    (1.7, "01:42", "Riyadh strike"),
    (13.5, "13:30", "Kyiv bridges"),
    (17.0, "~17:00", "Anthropic debut"),
    (21.0, "21:00", "Dow \u22121,101"),
]

# ------------------------------------------------------- illustrations
def _flag(draw, x, y, w, h, kind):
    """Tiny flat flag. kind: us | cn | ru | eu | de | ua | fr | uk."""
    if kind == "us":
        for i in range(7):
            draw.rectangle(box(x, y + i * h / 7, x + w, y + (i + 1) * h / 7),
                           fill=(176, 58, 46) if i % 2 == 0 else (255, 255, 255))
        draw.rectangle(box(x, y, x + w * 0.45, y + h * 0.55), fill=NAVY)
    elif kind == "cn":
        draw.rectangle(box(x, y, x + w, y + h), fill=(222, 41, 16))
        for sx, sy, r in [(0.22, 0.28, 2), (0.42, 0.20, 1.5), (0.48, 0.38, 1.5),
                          (0.42, 0.55, 1.5), (0.26, 0.52, 1.5)]:
            draw.ellipse(box(x + w * sx - r, y + h * sy - r,
                             x + w * sx + r, y + h * sy + r), fill=(255, 222, 0))
    elif kind == "ru":
        draw.rectangle(box(x, y, x + w, y + h / 3), fill=(255, 255, 255))
        draw.rectangle(box(x, y + h / 3, x + w, y + 2 * h / 3), fill=(0, 57, 166))
        draw.rectangle(box(x, y + 2 * h / 3, x + w, y + h), fill=(213, 0, 50))
    elif kind == "eu":
        draw.rectangle(box(x, y, x + w, y + h), fill=(0, 51, 153))
        for sx, sy in [(0.5, 0.2), (0.68, 0.35), (0.68, 0.65), (0.5, 0.8),
                       (0.32, 0.65), (0.32, 0.35)]:
            draw.ellipse(box(x + w * sx - 1, y + h * sy - 1,
                             x + w * sx + 1, y + h * sy + 1), fill=(255, 204, 0))
    elif kind == "de":
        draw.rectangle(box(x, y, x + w, y + h / 3), fill=(20, 20, 20))
        draw.rectangle(box(x, y + h / 3, x + w, y + 2 * h / 3), fill=(221, 0, 0))
        draw.rectangle(box(x, y + 2 * h / 3, x + w, y + h), fill=(255, 206, 0))
    elif kind == "ua":
        draw.rectangle(box(x, y, x + w, y + h / 2), fill=(0, 91, 187))
        draw.rectangle(box(x, y + h / 2, x + w, y + h), fill=(255, 213, 0))
    elif kind == "fr":
        draw.rectangle(box(x, y, x + w / 3, y + h), fill=(0, 85, 164))
        draw.rectangle(box(x + w / 3, y, x + 2 * w / 3, y + h),
                       fill=(255, 255, 255))
        draw.rectangle(box(x + 2 * w / 3, y, x + w, y + h), fill=(239, 65, 53))
    else:  # uk
        draw.rectangle(box(x, y, x + w, y + h), fill=(0, 36, 125))
        draw.rectangle(box(x + w * 0.42, y, x + w * 0.58, y + h),
                       fill=(255, 255, 255))
        draw.rectangle(box(x, y + h * 0.42, x + w, y + h * 0.58),
                       fill=(255, 255, 255))


def _chair(draw, x, y, w, h, col=(88, 80, 66)):
    """Empty angular chair: backrest + seat + legs."""
    draw.rectangle(box(x, y, x + w, y + h * 0.62), fill=col)
    draw.rectangle(box(x - w * 0.12, y + h * 0.62, x + w * 1.12, y + h * 0.74),
                   fill=col)
    draw.rectangle(box(x, y + h * 0.74, x + w * 0.12, y + h), fill=col)
    draw.rectangle(box(x + w * 0.88, y + h * 0.74, x + w, y + h), fill=col)


def _gavel(draw, x, y, s, col=(120, 80, 40)):
    """Small gavel: head + handle, angled."""
    draw.rectangle(box(x, y, x + s * 0.9, y + s * 0.32), fill=col)
    draw.rectangle(box(x + s * 0.32, y + s * 0.28, x + s * 0.48, y + s),
                   fill=col)


def paint(draw, n, x, y, w, h):
    """Flat scene art for story n, inside (x, y, w, h). No faces, no photos."""
    if n == 1:
        # Trilateral summit: dusk sky, Shenzhen skyline, long table,
        # three empty chairs, three folders, declaration sheet.
        sky(draw, x, y, w, h, (46, 64, 96), (232, 200, 150))
        base = y + h * 0.62
        towers = [(0.02, 0.30), (0.10, 0.44), (0.20, 0.26), (0.30, 0.52),
                  (0.42, 0.34), (0.52, 0.58), (0.62, 0.30), (0.72, 0.46),
                  (0.82, 0.28), (0.90, 0.40)]
        for fx, fh in towers:
            tx = x + w * fx
            tw = w * 0.07
            draw.rectangle(box(tx, base - h * fh, tx + tw, base),
                           fill=(30, 42, 66))
        # spire on the tallest tower
        sx = x + w * 0.52
        draw.polygon(pts((sx + w * 0.035, base - h * 0.58),
                         (sx + w * 0.02, base - h * 0.78),
                         (sx + w * 0.05, base - h * 0.78)), fill=(30, 42, 66))
        _dots(draw, x, base - h * 0.5, w, h * 0.5, (255, 220, 140), 9, 1.2,
              seed=7, fill=0.35)
        # table
        draw.rectangle(box(x, base, x + w, y + h), fill=(96, 62, 38))
        draw.rectangle(box(x, base, x + w, base + 3), fill=(150, 100, 60))
        # three empty chairs behind the table
        for cx in (0.16, 0.46, 0.76):
            _chair(draw, x + w * cx - 13, base - 30, 26, 30)
        # three folders on the table
        for i, (fx, kind, lab) in enumerate(
                [(0.14, "us", "US"), (0.44, "cn", "CHINA"),
                 (0.74, "ru", "RUSSIA")]):
            fx0 = x + w * fx - 16
            draw.rectangle(box(fx0, base + 12, fx0 + 32, base + 30),
                           fill=(240, 235, 220), outline=(60, 60, 60), width=S)
            _flag(draw, fx0 + 4, base + 15, 12, 8, kind)
            draw.text(xy(fx0 + 18, base + 15), lab, font=F(SANS_B, 7),
                      fill=INK)
    elif n == 2:
        # ICJ courtroom: wood panels, bench, scales of justice, 9-6, gavel.
        draw.rectangle(box(x, y, x + w, y + h), fill=(120, 80, 50))
        for i in range(6):
            px = x + i * w / 6
            draw.line([xy(px, y), xy(px, y + h * 0.55)], fill=(90, 58, 34),
                      width=S)
        draw.rectangle(box(x, y + h * 0.55, x + w, y + h), fill=(70, 45, 28))
        draw.rectangle(box(x, y + h * 0.55, x + w, y + h * 0.55 + 3),
                       fill=GOLD)
        # scales of justice
        cx, cy = x + w * 0.5, y + h * 0.30
        draw.rectangle(box(cx - 2, cy - 16, cx + 2, cy + 12), fill=GOLD)
        draw.line([xy(cx - 26, cy - 8), xy(cx + 26, cy - 8)], fill=GOLD,
                  width=2 * S)
        for sgn in (-1, 1):
            px = cx + sgn * 26
            draw.line([xy(px, cy - 8), xy(px, cy + 4)], fill=GOLD, width=S)
            draw.polygon(pts((px - 9, cy + 4), (px + 9, cy + 4),
                             (px, cy + 13)), fill=GOLD)
        draw.ellipse(box(cx - 4, cy - 20, cx + 4, cy - 12), fill=GOLD)
        # big 9-6 on the bench front
        centred(draw, x + w * 0.5, y + h * 0.66, "9\u20136",
                F(SERIF_B, 30), (255, 214, 130))
        _gavel(draw, x + w * 0.82, y + h * 0.72, 16)
    elif n == 3:
        # COP31 draft: a page with FOSSIL FUELS struck through, $120bn crossed.
        draw.rectangle(box(x, y, x + w, y + h), fill=(220, 228, 210))
        px, py, pw, ph = x + w * 0.12, y + 4, w * 0.76, h - 8
        draw.rectangle(box(px, py, px + pw, py + ph), fill=(255, 255, 255),
                       outline=(140, 140, 140), width=S)
        for j in range(3):
            draw.line([xy(px + 10, py + 10 + j * 6),
                       xy(px + pw - 10, py + 10 + j * 6)],
                      fill=(180, 180, 180), width=S)
        draw.text(xy(px + 10, py + 30), "FOSSIL FUELS", font=F(SANS_B, 15),
                  fill=INK)
        draw.line([xy(px + 8, py + 38), xy(px + pw - 8, py + 42)],
                  fill=RED, width=3 * S)
        draw.text(xy(px + 10, py + 48), "$120bn", font=F(SANS_B, 15),
                  fill=RED)
        draw.line([xy(px + 8, py + 52), xy(px + 52, py + 64)], fill=RED,
                  width=2 * S)
        draw.line([xy(px + 52, py + 52), xy(px + 8, py + 64)], fill=RED,
                  width=2 * S)
        draw.text(xy(px + 10, py + ph - 12), "80 / 144 paragraphs",
                  font=F(SANS, 9), fill=MUTED)
        draw.rectangle(box(px + pw - 52, py + 4, px + pw - 6, py + 18),
                       outline=RED, width=2 * S)
        draw.text(xy(px + pw - 48, py + 7), "DRAFT", font=F(SANS_B, 9),
                  fill=RED)
    elif n == 4:
        # Anthropic IPO: rising chart on navy, ANT chip.
        draw.rectangle(box(x, y, x + w, y + h), fill=(24, 48, 92))
        for gy in range(1, 4):
            draw.line([xy(x, y + h * gy / 4), xy(x + w, y + h * gy / 4)],
                      fill=(60, 90, 140), width=S)
        pts_up = [(0.06, 0.78), (0.25, 0.70), (0.42, 0.74), (0.58, 0.45),
                  (0.74, 0.38), (0.92, 0.16)]
        draw.line([xy(x + w * a, y + h * b) for a, b in pts_up],
                  fill=(60, 200, 120), width=3 * S)
        ax, ay = x + w * 0.92, y + h * 0.16
        draw.polygon(pts((ax - 7, ay + 2), (ax + 7, ay + 2), (ax, ay - 7)),
                     fill=(60, 200, 120))
        draw.text(xy(x + 8, y + 6), "$81.3bn", font=F(SANS_XB, 17),
                  fill=(255, 255, 255))
        draw.rectangle(box(x + w - 40, y + h - 18, x + w - 8, y + h - 6),
                       fill=(255, 255, 255))
        draw.text(xy(x + w - 36, y + h - 17), "ANT", font=F(SANS_B, 9),
                  fill=NAVY)
    elif n == 5:
        # GTA VI: night city, big VI.
        sky(draw, x, y, w, h, (40, 20, 70), (120, 40, 110))
        _stars(draw, x, y, w, h * 0.5, 14, seed=11)
        base = y + h
        for fx, fh in [(0.02, 0.5), (0.12, 0.72), (0.24, 0.45), (0.34, 0.8),
                       (0.48, 0.55), (0.60, 0.9), (0.74, 0.5), (0.84, 0.66)]:
            tx = x + w * fx
            draw.rectangle(box(tx, base - h * fh, tx + w * 0.09, base),
                           fill=(20, 10, 35))
        _dots(draw, x, base - h * 0.8, w, h * 0.8, (255, 200, 90), 8, 1,
              seed=5, fill=0.3)
        draw.text(xy(x + w * 0.60, y + h * 0.06), "VI",
                  font=F(SERIF_B, 30), fill=(255, 90, 180))
    elif n == 6:
        # Cyclone Akvan: spiral over slate sea, rain.
        draw.rectangle(box(x, y, x + w, y + h), fill=(70, 100, 130))
        cx, cy = x + w * 0.42, y + h * 0.52
        spiral = []
        for k in range(0, 61):
            ang = k * 0.22
            r = 2 + k * 0.42
            spiral.append((cx + r * math.cos(ang), cy + r * math.sin(ang) * 0.8))
        draw.line([xy(a, b) for a, b in spiral], fill=(255, 255, 255),
                  width=2 * S)
        for i in range(8):
            rx = x + w * (0.08 + i * 0.11)
            draw.line([xy(rx, y + 4), xy(rx - 3, y + 14)], fill=(200, 220, 240),
                      width=S)
        draw.text(xy(x + w * 0.68, y + 6), "80,000+", font=F(SANS_XB, 13),
                  fill=(255, 255, 255))
    elif n == 7:
        # Kerch bridge: deck with a broken gap, smoke, warning triangle.
        draw.rectangle(box(x, y, x + w, y + h), fill=(200, 205, 210))
        draw.rectangle(box(x, y + h * 0.62, x + w, y + h), fill=(90, 120, 150))
        deck_y = y + h * 0.45
        draw.rectangle(box(x, deck_y, x + w * 0.44, deck_y + 5), fill=(60, 60, 60))
        draw.rectangle(box(x + w * 0.56, deck_y, x + w, deck_y + 5),
                       fill=(60, 60, 60))
        for fx in (0.12, 0.30, 0.70, 0.88):
            draw.rectangle(box(x + w * fx, deck_y + 5, x + w * fx + 3,
                               y + h * 0.62), fill=(60, 60, 60))
        for i, (sx, sy, r) in enumerate([(0.50, 0.30, 7), (0.54, 0.22, 9),
                                         (0.47, 0.20, 6)]):
            draw.ellipse(box(x + w * sx - r, y + h * sy - r,
                             x + w * sx + r, y + h * sy + r),
                         fill=(120, 120, 120))
        draw.polygon(pts((x + w * 0.50, deck_y - 16),
                         (x + w * 0.44, deck_y - 2),
                         (x + w * 0.56, deck_y - 2)), fill=(198, 60, 40))
        draw.text(xy(x + w * 0.485, deck_y - 13), "!", font=F(SANS_B, 9),
                  fill=(255, 255, 255))
    elif n == 8:
        # Riyadh PIF Tower: tall dark tower, impact burst near the top.
        sky(draw, x, y, w, h, (60, 50, 80), (240, 180, 120))
        tx, tw = x + w * 0.44, w * 0.14
        draw.polygon(pts((tx, y + h), (tx + 3, y + h * 0.10),
                         (tx + tw - 3, y + h * 0.10), (tx + tw, y + h)),
                     fill=(35, 35, 45))
        _dots(draw, tx + 2, y + h * 0.14, tw - 4, h * 0.8, (255, 210, 120),
              7, 1, seed=9, fill=0.5)
        _burst(draw, tx + tw * 0.5, y + h * 0.22, 9, (255, 200, 60))
        draw.line([xy(tx + tw * 0.5, y + h * 0.22),
                   xy(tx + tw * 0.5 - 8, y + h * 0.38)], fill=(255, 255, 255),
                  width=S)
        draw.text(xy(x + 6, y + 4), "PIF", font=F(SANS_B, 10),
                  fill=(255, 255, 255))
    elif n == 9:
        # Colombia strike: crowd silhouettes and placards.
        draw.rectangle(box(x, y, x + w, y + h), fill=(235, 210, 170))
        for i, hx in enumerate([0.08, 0.22, 0.36, 0.50, 0.64, 0.78, 0.92]):
            cx = x + w * hx
            cy = y + h * (0.55 + (i % 3) * 0.06)
            draw.ellipse(box(cx - 6, cy - 6, cx + 6, cy + 6), fill=(50, 45, 40))
            draw.rectangle(box(cx - 9, cy + 5, cx + 9, y + h), fill=(50, 45, 40))
        for px, py in [(0.22, 0.38), (0.50, 0.32), (0.78, 0.40)]:
            sx = x + w * px
            sy = y + h * py
            draw.line([xy(sx, sy + 12), xy(sx, sy + 26)], fill=(80, 70, 60),
                      width=S)
            draw.rectangle(box(sx - 10, sy, sx + 10, sy + 12),
                           fill=(255, 255, 255), outline=(50, 45, 40), width=S)
        draw.rectangle(box(x + w * 0.30, y + h - 12, x + w * 0.70, y + h - 4),
                       fill=RED)
    elif n == 10:
        # Australia jobs: red down-trend, big 4.9%.
        draw.rectangle(box(x, y, x + w, y + h), fill=(245, 240, 230))
        for gy in range(1, 4):
            draw.line([xy(x, y + h * gy / 4), xy(x + w, y + h * gy / 4)],
                      fill=(220, 215, 200), width=S)
        pts_dn = [(0.06, 0.25), (0.25, 0.32), (0.45, 0.30), (0.65, 0.55),
                  (0.85, 0.72)]
        draw.line([xy(x + w * a, y + h * b) for a, b in pts_dn],
                  fill=(198, 60, 40), width=3 * S)
        ax, ay = x + w * 0.85, y + h * 0.72
        draw.polygon(pts((ax - 7, ay - 2), (ax + 7, ay - 2), (ax, ay + 7)),
                     fill=(198, 60, 40))
        draw.text(xy(x + 8, y + 4), "4.9%", font=F(SANS_XB, 17), fill=RED)
    elif n == 11:
        # Korea CSAT: exam sheet and pencil.
        draw.rectangle(box(x, y, x + w, y + h), fill=(235, 230, 215))
        px, py, pw, ph = x + w * 0.08, y + 5, w * 0.55, h - 10
        draw.rectangle(box(px, py, px + pw, py + ph), fill=(255, 255, 255),
                       outline=(140, 140, 140), width=S)
        for j in range(4):
            draw.line([xy(px + 7, py + 9 + j * 7),
                       xy(px + pw - 7, py + 9 + j * 7)],
                      fill=(170, 170, 170), width=S)
        draw.polygon(pts((x + w * 0.70, y + h * 0.85),
                         (x + w * 0.78, y + h * 0.80),
                         (x + w * 0.95, y + h * 0.18),
                         (x + w * 0.88, y + h * 0.12)), fill=(255, 200, 40))
        draw.polygon(pts((x + w * 0.95, y + h * 0.18),
                         (x + w * 0.88, y + h * 0.12),
                         (x + w * 0.92, y + h * 0.04)), fill=(240, 180, 160))
        draw.text(xy(x + w * 0.68, y + 4), "551,864", font=F(SANS_XB, 12),
                  fill=INK)
    elif n == 12:
        # Indonesia law: document with red seal, gavel, 18 YRS chip.
        draw.rectangle(box(x, y, x + w, y + h), fill=(225, 220, 205))
        px, py, pw, ph = x + w * 0.10, y + 6, w * 0.52, h - 12
        draw.rectangle(box(px, py, px + pw, py + ph), fill=(255, 255, 255),
                       outline=(140, 140, 140), width=S)
        for j in range(4):
            draw.line([xy(px + 7, py + 9 + j * 7),
                       xy(px + pw - 7, py + 9 + j * 7)],
                      fill=(170, 170, 170), width=S)
        draw.ellipse(box(px + pw - 22, py + ph - 20, px + pw - 8, py + ph - 6),
                     fill=RED)
        _gavel(draw, x + w * 0.68, y + h * 0.45, 18)
        draw.rectangle(box(x + w * 0.66, y + 5, x + w * 0.97, y + 17),
                       fill=INK)
        draw.text(xy(x + w * 0.69, y + 7), "18 YRS", font=F(SANS_B, 9),
                  fill=(255, 255, 255))
    elif n == 13:
        # Berlin: chancellery block and a row of small flags.
        draw.rectangle(box(x, y, x + w, y + h), fill=(215, 220, 225))
        bx, by, bw, bh = x + w * 0.06, y + h * 0.28, w * 0.88, h * 0.60
        draw.rectangle(box(bx, by, bx + bw, by + bh), fill=(120, 125, 130))
        for r in range(2):
            for c in range(8):
                wx = bx + 8 + c * (bw - 16) / 8
                wy = by + 8 + r * (bh - 16) / 2
                draw.rectangle(box(wx, wy, wx + (bw - 16) / 8 - 5,
                                   wy + (bh - 16) / 2 - 6),
                               fill=(230, 225, 200))
        for i, kind in enumerate(["eu", "de", "ua", "fr", "uk"]):
            fx = x + w * (0.10 + i * 0.17)
            draw.line([xy(fx + 7, y + 4), xy(fx + 7, y + 20)], fill=(80, 80, 80),
                      width=S)
            _flag(draw, fx, y + 4, 14, 9, kind)

# ------------------------------------------------------------------- layout
def rigor_counts():
    """Verification counts across all 40 stories (computed, not typed)."""
    n_conf = sum(1 for m in MAINS if m[7] == "CONFIRMED")
    n_conf += sum(1 for a in ALSO if "[CLAIM]" not in a[2]
                  and "[FORECAST]" not in a[2])
    n_claim = sum(1 for m in MAINS if m[7] == "CLAIM")
    n_claim += sum(1 for a in ALSO if "[CLAIM]" in a[2])
    n_fore = sum(1 for m in MAINS if m[7] == "FORECAST")
    n_fore += sum(1 for a in ALSO if "[FORECAST]" in a[2])
    return n_conf, n_claim, n_fore


def main():
    img = Image.new("RGB", (W * S, H * S), PAPER)
    d = ImageDraw.Draw(img)
    MX = 32  # side margin (logical units)

    # ---- masthead ----
    d.text(xy(MX, 36), "THE WORLD IN ONE DAY", font=F(SANS_B, 12), fill=RED)
    d.text(xy(MX, 52), "Thursday 19 November 2026", font=F(SERIF_B, 46),
           fill=INK)
    count = "40 STORIES \u00b7 7 REGIONS \u00b7 ONE DAY"
    cw = d.textlength(count, font=F(SANS_B, 12))
    d.text(xy(W - MX - cw / S, 38), count, font=F(SANS_B, 12), fill=MUTED)
    # red date badge, bottom-right of the masthead
    bx0, by0, bx1, by1 = W - MX - 118, 54, W - MX, 108
    d.rectangle(box(bx0, by0, bx1, by1), fill=RED, outline=GOLD, width=2 * S)
    centred(d, (bx0 + bx1) // 2, by0 + 7, "19 NOV", F(SANS_B, 22),
            (255, 255, 255))
    centred(d, (bx0 + bx1) // 2, by0 + 34, "THU \u00b7 2026", F(SANS_B, 9),
            (255, 255, 255))
    d.rectangle(box(MX, 114, W - MX, 117), fill=RED)

    # ---- day in numbers strip ----
    d.text(xy(MX, 130), "THE DAY", font=F(SANS_B, 12), fill=INK)
    d.text(xy(MX, 146), "IN NUMBERS", font=F(SANS_B, 12), fill=INK)
    fx = 180
    for num, lab in NUMBERS:
        nf = F(SERIF_B, 20)
        d.text(xy(fx, 124), num, font=nf, fill=INK)
        d.text(xy(fx, 148), lab, font=F(SANS, 10), fill=MUTED)
        fx += 112
    d.line([xy(MX, 170), xy(W - MX, 170)], fill=PANEL_LINE, width=S)

    # ---- RIGOR BAR ----
    n_conf, n_claim, n_fore = rigor_counts()
    d.text(xy(MX, 178), "RIGOR", font=F(SANS_B, 10), fill=INK)
    bar_x, bar_y, bar_w, bar_h = 88, 180, 300, 12
    total = n_conf + n_claim + n_fore
    x = bar_x
    for cnt, col in ((n_conf, CONFIRMED_COL), (n_claim, CLAIM_COL),
                     (n_fore, FORECAST_COL)):
        seg = bar_w * cnt / total
        if seg >= 1:
            d.rectangle(box(x, bar_y, x + seg, bar_y + bar_h), fill=col)
        x += seg
    d.rectangle(box(bar_x, bar_y, bar_x + bar_w, bar_y + bar_h),
                outline=INK, width=S)
    rig = (f"{n_conf} CONFIRMED \u00b7 {n_claim} CLAIM \u00b7 {n_fore} FORECAST"
           f" \u2014 every main verified; the one claim is flagged [CLAIM].")
    d.text(xy(400, 178), rig, font=F(SANS_B, 11), fill=INK)

    # ---- 3 leads ----
    ly = 198
    lead_w = 314
    lead_h = 200
    for i, m in enumerate(MAINS[:3]):
        n, region, cat, tag, head, deck, src, status, _lon, _lat = m
        x = MX + i * (lead_w + 9)
        col = CAT_COLOUR[cat]
        paint(d, n, x, ly, lead_w, 92)
        ty = ly + 96
        badge(d, x + 12, ty + 7, n, REGION_COLOUR[region], r=11)
        kick = f"{region} \u00b7 {tag}"
        if n == 1:
            kick = "\u2605 TOP STORY \u00b7 " + kick
        d.text(xy(x + 28, ty), kick, font=F(SANS_B, 11), fill=col)
        lines = balance_two(d, head, F(SERIF_B, 22), lead_w) or \
            fit_lines(d, head, F(SERIF_B, 22), lead_w, 2)
        text_block(d, x, ty + 18, lines, F(SERIF_B, 22), INK, 24)
        dl = fit_lines(d, deck, F(SANS, 11.5), lead_w, 2)
        text_block(d, x, ty + 18 + len(lines) * 24 + 3, dl, F(SANS, 11.5),
                   (60, 60, 60), 13)
        mark = "\u2713" if status == "CONFIRMED" else "?"
        d.text(xy(x, ty + 18 + len(lines) * 24 + 3 + len(dl) * 13 + 2),
               f"{mark} {status} \u00b7 {src}", font=F(SANS_B, 9.5),
               fill=CONFIRMED_COL if status == "CONFIRMED" else CLAIM_COL)

    # ---- mains grid: 2 rows x 5 ----
    gy = 402
    col_w = 185
    row_h = 142
    for ri in range(2):
        for ci in range(5):
            m = MAINS[3 + ri * 5 + ci]
            n, region, cat, tag, head, deck, src, status, _lon, _lat = m
            x = MX + ci * (col_w + 8.75)
            y0 = gy + ri * (row_h + 8)
            col = CAT_COLOUR[cat]
            paint(d, n, x, y0, col_w, 52)
            ty = y0 + 56
            badge(d, x + 10, ty + 6, n, REGION_COLOUR[region], r=10)
            d.text(xy(x + 24, ty), f"{region} \u00b7 {tag}",
                   font=F(SANS_B, 9), fill=col)
            lines = balance_two(d, head, F(SANS_B, 14), col_w) or \
                fit_lines(d, head, F(SANS_B, 14), col_w, 2)
            text_block(d, x, ty + 16, lines, F(SANS_B, 14), INK, 16)
            dl = fit_lines(d, deck, F(SANS, 11), col_w, 2)
            text_block(d, x, ty + 16 + len(lines) * 16 + 2, dl, F(SANS, 11),
                       (60, 60, 60), 12.5)
            mark = "\u2713" if status == "CONFIRMED" else "?"
            d.text(xy(x, ty + 16 + len(lines) * 16 + 2 + len(dl) * 12.5 + 2),
                   f"{mark} {status} \u00b7 {src}", font=F(SANS_B, 9),
                   fill=CONFIRMED_COL if status == "CONFIRMED" else CLAIM_COL)

    # ---- bottom: map + also-on ----
    by = 698
    d.line([xy(MX, by), xy(W - MX, by)], fill=GOLD, width=2 * S)
    d.text(xy(MX, by + 6), "WHERE IT HAPPENED", font=F(SANS_B, 12), fill=NAVY)
    d.text(xy(400, by + 6), "ALSO ON THURSDAY 19 NOVEMBER",
           font=F(SANS_B, 12), fill=NAVY)
    map_y = by + 22
    map_h = 150
    draw_map(d, MX, map_y, 352, map_h)
    d.text(xy(MX, map_y + map_h + 5),
           "Numbered pins: stories 1\u201313. Dots: briefs 14\u201340.",
           font=F(SANS, 9.5), fill=MUTED)
    # also-on: two columns, complete one-liners
    ax = 400
    acol_w = 290
    for ci in range(2):
        items = ALSO[ci * 14:(ci + 1) * 14]
        xx = ax + ci * (acol_w + 12)
        for j, (n, region, text, _lon, _lat) in enumerate(items):
            yy = map_y + j * 11.5
            col = REGION_COLOUR[region]
            fnt = F(SANS_B, 11)
            tw = d.textlength(f"{n}", font=fnt)
            d.text(xy(xx, yy), f"{n}", font=fnt, fill=col)
            d.text(xy(xx + tw / S + 5, yy), text, font=F(SANS, 11), fill=INK)

    # ---- verdict + timeline ----
    vy = 886
    d.text(xy(MX, vy + 2), "THE VERDICT", font=F(SANS_B, 11), fill=RED)
    vw = d.textlength("THE VERDICT", font=F(SANS_B, 11))
    d.text(xy(MX + vw / S + 10, vy + 1), VERDICT, font=F(SANS, 15), fill=INK)
    # UTC timeline rail
    rail_y = vy + 30
    d.text(xy(MX, rail_y - 2), "19 NOV \u00b7 UTC", font=F(SANS_B, 9), fill=MUTED)
    rx0, rx1 = 130, W - MX
    d.line([xy(rx0, rail_y + 3), xy(rx1, rail_y + 3)], fill=PANEL_LINE,
           width=2 * S)
    for hour in (0, 6, 12, 18, 24):
        tx = rx0 + (rx1 - rx0) * hour / 24
        d.line([xy(tx, rail_y), xy(tx, rail_y + 6)], fill=MUTED, width=S)
        lab = f"{hour:02d}:00"
        lw = d.textlength(lab, font=F(SANS, 8))
        d.text(xy(tx - lw / S / 2, rail_y + 8), lab, font=F(SANS, 8),
               fill=MUTED)
    for hour, tlab, text in TIMELINE:
        tx = rx0 + (rx1 - rx0) * hour / 24
        draw_dot = d.ellipse(box(tx - 4, rail_y - 1, tx + 4, rail_y + 7),
                             fill=RED, outline=(255, 255, 255), width=S)
        lab = f"{tlab} {text}"
        lw = d.textlength(lab, font=F(SANS_B, 8.5))
        d.text(xy(tx - lw / S / 2, rail_y - 13), lab, font=F(SANS_B, 8.5),
               fill=INK)

    # ---- DATE CHECK footer ----
    fy = 938
    d.rectangle(box(MX, fy, W - MX, fy + 44), fill=(246, 228, 226),
                outline=RED, width=S)
    d.text(xy(MX + 8, fy + 4), "DATE CHECK", font=F(SANS_B, 10.5), fill=RED)
    dc = wrap(d, DATE_CHECK, F(SANS, 10.5), W - 2 * MX - 110)
    text_block(d, MX + 96, fy + 4, dc, F(SANS, 10.5), INK, 13)
    sy = fy + 48
    centred(d, W // 2, sy, SOURCES, F(SANS, 9.5), MUTED)

    out = os.path.join(ROOT, "entry.png")
    small = img.resize((W, H), Image.LANCZOS)
    small.save(out)
    print("saved", out, small.size, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
