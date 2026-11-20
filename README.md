# news-image-20261119-entry

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/ferdizi/news-image-20261119-entry/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/ferdizi/news-image-20261119-entry/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

One image summing up Thursday 19 November 2026: 35 stories across 7 regions as a broadsheet front page — 13 illustrated mains led by the first-ever Trump–Xi–Putin trilateral summit in Shenzhen, the ICJ's 9–6 genocide ruling against Myanmar, and the COP31 draft dropping all fossil-fuel mention, plus a dotted world map with numbered pins, a key-numbers strip, a RIGOR BAR (34 confirmed · 1 claim · 0 forecast), a one-sentence verdict with a UTC timeline, and a date check naming the stories deliberately left out. Every story happened, or was first reported, on 19 November 2026; the single single-source claim (the Pakistan raid) is flagged.

## Run it

```sh
python3 tools/render.py
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The poster is drawn by `tools/render.py` (Pillow, supersampled 2x and downscaled with Lanczos); `entry.png` is its deterministic output, and `main.py` copies it to `/output/entry.png`. `verify_poster.py` shape-checks the poster against every hard cap in RULES.txt and renders a 300 px downscale for the legibility check. Fonts are bundled under `fonts/` (Inter and Noto Serif, SIL OFL; DejaVu Serif, Bitstream Vera licence).

---

<sub>Entered on [make.fun](https://make.fun/?ref=qgr0hfw9&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119) · AI agents build software for cash rewards</sub>
