#!/usr/bin/env python3
"""Shape-check the v2 19 November poster against the hard caps in RULES.txt.

Checks the built entry.png next to this file: a whole PNG, exactly
1024 by 1024 pixels, at most 1 MiB, no metadata chunks; the masthead
names Thursday 19 November 2026; 13 numbered mains and 22 also-on items
(35 stories total); the region bar sums to 35; 6 figures in the
key-numbers strip; the RIGOR bar counts sum to 35 (34 CONFIRMED,
1 CLAIM, 0 FORECAST); the DATE CHECK names the excluded stories; no
wrong-date story sits in the mains; every also-on one-liner fits its
column in one line; every headline and deck fits in two lines; and two
builds are byte-identical. Also writes a 300 px downscale for the
legibility check the judge applies. Exit 0 only when every cap passes.

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
    print(f"[{mark}] {name}" + (f" \u2014 {detail}" if detail else ""))
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

    spec = importlib.util.spec_from_file_location("render19v2", RENDER)
    rr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rr)

    check("13 mains in data", len(rr.MAINS) == 13, f"got {len(rr.MAINS)}")
    check("22 also-on items", len(rr.ALSO) == 22, f"got {len(rr.ALSO)}")
    check("35 stories total", len(rr.MAINS) + len(rr.ALSO) == 35)
    check("region bar sums to 35",
          sum(c for _r, c in rr.REGION_BAR) == 35,
          str(rr.REGION_BAR))
    check("6 numbers in strip", len(rr.NUMBERS) == 6)
    nc, nk, nf = rr.rigor_counts()
    check("RIGOR counts sum to 35", nc + nk + nf == 35,
          f"{nc} CONFIRMED, {nk} CLAIM, {nf} FORECAST")
    check("RIGOR 34 confirmed", nc == 34, f"got {nc}")
    check("RIGOR 1 claim flagged", nk == 1, f"got {nk}")
    check("RIGOR 0 forecast", nf == 0, f"got {nf}")

    mains_src = str(rr.MAINS)
    for bad in ("VAN GOGH", "NATURE", "PEW", "NVIDIA", "VOYAGER"):
        check(f"no {bad} in mains", bad not in mains_src)
    check("DATE CHECK names the excluded stories",
          "Van Gogh" in rr.DATE_CHECK and "Nature" in rr.DATE_CHECK
          and "Pew" in rr.DATE_CHECK and "Kyiv" in rr.DATE_CHECK)
    check("DATE CHECK flags UK inflation inversion",
          "ROSE to 3.6%" in rr.DATE_CHECK)
    check("verdict present", "THE VERDICT" in rr.VERDICT)
    check("timeline has 4 entries", len(rr.TIMELINE) == 4)
    check("footer note present", "drawn in code" in rr.FOOTER_NOTE)
    check("sources line present", "Reuters, AP, AFP, BBC" in rr.SOURCES)

    with open(RENDER, encoding="utf-8") as fh:
        src = fh.read()
    check("date named in builder", "Thursday 19 November 2026" in src)
    check("masthead tagline drawn", '"THE WORLD IN ONE DAY"' in src)
    check("DATE CHECK footer drawn", "DATE_CHECK = (" in src)
    check("numbers strip drawn", '"PRESIDENTS AT ONE TABLE"' in src)
    check("RIGOR BAR drawn", "rigor_counts()" in src
          and "RIGOR" in src)
    check("region bar drawn", "REGION_BAR" in src)
    check("dotted map drawn", "draw_map(d, MX, y, map_w, map_h)" in src)
    check("verdict drawn", "draw_verdict_timeline" in src)
    check("footer sources", "Sources: Reuters, AP, AFP, BBC" in src)
    check("bundled Inter used", "Inter-Regular.otf" in src
          and "Inter-Bold.otf" in src)
    check("bundled Noto Serif used", "NotoSerif-Bold.ttf" in src)

    # Every also-on one-liner must fit its column (307 px) at 11 pt,
    # number included — otherwise it is cut off at the column edge.
    probe = Image.new("RGB", (10, 10))
    d = ImageDraw.Draw(probe)
    fnt_n = ImageFont.truetype(os.path.join(FONTS, "Inter-Bold.otf"), 22)
    fnt_t = ImageFont.truetype(os.path.join(FONTS, "Inter-Regular.otf"),
                               22)
    too_long = []
    for n, _region, text, _lon, _lat in rr.ALSO:
        w = (d.textlength(str(n) + ".", font=fnt_n) + 5 * 2
             + d.textlength(text, font=fnt_t)) / 2
        if w > 307:
            too_long.append((n, round(w)))
    check("all also-on lines fit one line", not too_long, str(too_long))

    # Every headline and deck must fit in two lines (no truncation).
    def fits_two(text, fnt_path, size, max_w):
        fnt = ImageFont.truetype(fnt_path, size * 2)
        lines = rr.wrap(d, text, fnt, max_w)
        return len(lines) <= 2

    bad_heads = []
    for m in rr.MAINS:
        n = m[0]
        if n <= 3:
            if not fits_two(m[4], os.path.join(FONTS, "NotoSerif-Bold.ttf"),
                            19, 317 - 20):
                bad_heads.append(("head", n))
            if not fits_two(m[5], os.path.join(FONTS, "Inter-Regular.otf"),
                            11, 317 - 20):
                bad_heads.append(("deck", n))
        else:
            if not fits_two(m[4], os.path.join(FONTS, "Inter-Bold.otf"),
                            13, 187 - 14):
                bad_heads.append(("head", n))
            if not fits_two(m[5], os.path.join(FONTS, "Inter-Regular.otf"),
                            10.5, 187 - 14):
                bad_heads.append(("deck", n))
    check("all headlines and decks fit in two lines", not bad_heads,
          str(bad_heads))

    # Determinism: two builds must be byte-identical.
    subprocess.run([sys.executable, RENDER], cwd=HERE, check=True,
                   capture_output=True)
    h1 = hashlib.sha256(open(PNG, "rb").read()).hexdigest()
    subprocess.run([sys.executable, RENDER], cwd=HERE, check=True,
                   capture_output=True)
    h2 = hashlib.sha256(open(PNG, "rb").read()).hexdigest()
    check("two builds byte-identical", h1 == h2, h1[:12])

    # main.py must copy entry.png to the output dir, twice identical.
    for outdir in ("/tmp/ni19-out-a", "/tmp/ni19-out-b"):
        env = dict(os.environ, MAKEFUN_OUTPUT_DIR=outdir)
        subprocess.run([sys.executable, "main.py"], cwd=HERE, check=True,
                       capture_output=True, env=env)
    ha = hashlib.sha256(open("/tmp/ni19-out-a/entry.png", "rb")
                        .read()).hexdigest()
    hb = hashlib.sha256(open("/tmp/ni19-out-b/entry.png", "rb")
                        .read()).hexdigest()
    check("main.py copies entry.png identically", ha == hb == h2, ha[:12])

    small = img.resize((300, 300), Image.LANCZOS)
    thumb = "/tmp/ni19-v2-300px.png"
    small.save(thumb)
    print(f"[info] 300px legibility render written to {thumb}")

    if failures:
        print(f"{len(failures)} cap(s) failed")
        sys.exit(1)
    print("all caps pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
