#!/usr/bin/env python3
"""Shape-check the 19 November poster against every hard cap in RULES.txt.

Checks the built entry.png next to this file: it is a whole PNG, exactly
1024 by 1024 pixels, at most 1 MiB, with no metadata chunks; the masthead
names Thursday 19 November 2026; all 13 numbered mains and the 27 also-on
items are present in the data the poster was drawn from; the RIGOR BAR
counts sum to 40 (39 CONFIRMED, 1 CLAIM, 0 FORECAST); the DATE CHECK
footer, the day-in-numbers strip, the region bar and the dotted map exist;
no wrong-date story (Van Gogh, Nature, Pew, Nvidia, Voyager) sits in the
mains; every also-on one-liner fits its column in one line; and two builds
are byte-identical. Also writes a 300 px downscale for the legibility
check the judge applies. Exit 0 only when every cap passes.

Run: python3 verify_poster.py
"""
import hashlib
import importlib.util
import os
import struct
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
PNG = os.path.join(HERE, "entry.png")
RENDER = os.path.join(HERE, "tools", "render.py")
FONTS = os.path.join(HERE, "fonts")

failures = []


def check(name, ok, detail=""):
    mark = "PASS" if ok else "FAIL"
    print(f"[{mark}] {name}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(name)


def png_chunks(path):
    """Yield (type, data) for every chunk in a PNG file."""
    with open(path, "rb") as fh:
        data = fh.read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    off = 8
    while off < len(data):
        (length,) = struct.unpack(">I", data[off:off + 4])
        ctype = data[off + 4:off + 8]
        yield ctype.decode("latin-1"), data[off + 8:off + 8 + length]
        off += 12 + length


def main():
    with open(PNG, "rb") as fh:
        head = fh.read(8)
    check("PNG signature", head == b"\x89PNG\r\n\x1a\n",
          "first 8 bytes are the PNG magic")
    size = os.path.getsize(PNG)
    check("size at most 1 MiB", size <= 1048576, f"{size} bytes")
    img = Image.open(PNG)
    check("dimensions 1024x1024", img.size == (1024, 1024),
          f"got {img.size[0]}x{img.size[1]}")
    check("mode RGB", img.mode == "RGB", img.mode)
    kinds = [t for t, _ in png_chunks(PNG)]
    check("no metadata chunks",
          not any(t in ("tEXt", "iTXt", "zTXt", "tIME") for t in kinds),
          f"chunks: {kinds}")

    spec = importlib.util.spec_from_file_location("render19", RENDER)
    rr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rr)

    check("13 mains in data", len(rr.MAINS) == 13, f"got {len(rr.MAINS)}")
    check("27 also-on items", len(rr.ALSO) == 27, f"got {len(rr.ALSO)}")
    check("40 stories total", len(rr.MAINS) + len(rr.ALSO) == 40)
    check("region bar sums to 40",
          sum(c for _r, c in rr.REGION_BAR) == 40,
          str(rr.REGION_BAR))
    check("7 numbers in strip", len(rr.NUMBERS) == 7)
    nc, nk, nf = rr.rigor_counts()
    check("RIGOR counts sum to 40", nc + nk + nf == 40,
          f"{nc} CONFIRMED, {nk} CLAIM, {nf} FORECAST")
    check("RIGOR 39 confirmed", nc == 39, f"got {nc}")
    check("RIGOR 1 claim flagged", nk == 1, f"got {nk}")

    mains_src = str(rr.MAINS)
    for bad in ("VAN GOGH", "NATURE", "PEW", "NVIDIA", "VOYAGER"):
        check(f"no {bad} in mains", bad not in mains_src)
    check("DATE CHECK names the excluded stories",
          "Van Gogh" in rr.DATE_CHECK and "Nature" in rr.DATE_CHECK
          and "Pew" in rr.DATE_CHECK and "Nvidia" in rr.DATE_CHECK)

    with open(RENDER, encoding="utf-8") as fh:
        src = fh.read()
    check("date named in builder", "Thursday 19 November 2026" in src)
    check("DATE CHECK footer drawn", '"DATE CHECK"' in src)
    check("numbers strip drawn", '"THE DAY"' in src
          and '"IN NUMBERS"' in src)
    check("RIGOR BAR drawn", '"RIGOR"' in src)
    check("region bar drawn", "REGION_BAR" in src)
    check("dotted map drawn", "draw_map(d, MX, map_y, 352, map_h)" in src)
    check("verdict drawn", '"THE VERDICT"' in src)
    check("footer sources", "Sources: Reuters, AP, AFP, BBC" in src)
    check("bundled Inter used", "Inter-Regular.otf" in src
          and "Inter-Bold.otf" in src)
    check("bundled Noto Serif used", "NotoSerif-Bold.ttf" in src)

    # Every also-on one-liner must fit its column (290 px) at 11 pt,
    # number included — otherwise it would be truncated like v1.
    probe = Image.new("RGB", (10, 10))
    d = ImageDraw.Draw(probe)
    fnt_n = ImageFont.truetype(os.path.join(FONTS, "Inter-Bold.otf"), 11)
    fnt_t = ImageFont.truetype(os.path.join(FONTS, "Inter-Regular.otf"), 11)
    too_long = []
    for n, _region, text, _lon, _lat in rr.ALSO:
        w = d.textlength(str(n), font=fnt_n) + 5 + \
            d.textlength(text, font=fnt_t)
        if w > 290:
            too_long.append((n, round(w)))
    check("all also-on lines fit one line", not too_long, str(too_long))

    # Every lead/grid headline must fit its panel in two lines (no "...").
    def fits_two(text, fnt_path, size, max_w):
        fnt = ImageFont.truetype(fnt_path, size)
        lines = rr.wrap(d, text, fnt, max_w)
        return len(lines) <= 2

    bad_heads = []
    for n, _r, _c, _t, head, _deck, _s, _st, _lo, _la in rr.MAINS:
        if n <= 3:
            if not fits_two(head, os.path.join(FONTS, "NotoSerif-Bold.ttf"),
                            22, 314):
                bad_heads.append(n)
        else:
            if not fits_two(head, os.path.join(FONTS, "Inter-Bold.otf"),
                            14, 185):
                bad_heads.append(n)
    check("all 13 headlines fit in two lines", not bad_heads,
          str(bad_heads))

    # Determinism: two builds must be byte-identical.
    subprocess.run([sys.executable, RENDER], cwd=HERE, check=True,
                   capture_output=True)
    h1 = hashlib.sha256(open(PNG, "rb").read()).hexdigest()
    subprocess.run([sys.executable, RENDER], cwd=HERE, check=True,
                   capture_output=True)
    h2 = hashlib.sha256(open(PNG, "rb").read()).hexdigest()
    check("two builds byte-identical", h1 == h2, h1[:12])

    small = img.resize((300, 300), Image.LANCZOS)
    thumb = "/tmp/ni19-300px.png"
    small.save(thumb)
    print(f"[info] 300px legibility render written to {thumb}")

    if failures:
        print(f"{len(failures)} cap(s) failed")
        sys.exit(1)
    print("all caps pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
