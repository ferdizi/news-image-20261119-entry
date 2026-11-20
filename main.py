#!/usr/bin/env python3
"""Entry program for news-image-20261119.

The poster (entry.png, drawn by tools/render.py) sits next to this file.
This program copies it to the output directory the grader reads:
 /output/entry.png inside the grading container, or $MAKEFUN_OUTPUT_DIR
when set (handy for a local run: MAKEFUN_OUTPUT_DIR=out python3 main.py).
The file must stay a PNG or JPEG of at most 1 MiB and 1024x1024 px.
Standard library only; no network.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")


def main():
    os.makedirs(OUT, exist_ok=True)
    shutil.copyfile(os.path.join(HERE, "entry.png"),
                    os.path.join(OUT, "entry.png"))


if __name__ == "__main__":
    main()
