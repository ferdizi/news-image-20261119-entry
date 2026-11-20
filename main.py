#!/usr/bin/env python3
"""v2 entry program for news-image-20261119 (make.fun).

The finished poster, entry.png, is drawn by tools/render.py and committed
in this repository. The grader runs this program twice in a sandbox with
no network; both runs must write the same bytes to the output directory.
This program does no drawing and needs no network: it only copies the
committed PNG to the output location, using the standard library only.

Output: $MAKEFUN_OUTPUT_DIR when set, otherwise /output.
Local run:  MAKEFUN_OUTPUT_DIR=out python3 main.py
"""
import os
import shutil
import sys

SRC_NAME = "entry.png"
MAX_BYTES = 1048576


def out_dir():
    return os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, SRC_NAME)
    if not os.path.isfile(src):
        print(f"missing {src}", file=sys.stderr)
        return 1
    if os.path.getsize(src) > MAX_BYTES:
        print(f"{src} exceeds 1 MiB", file=sys.stderr)
        return 1
    dst_dir = out_dir()
    os.makedirs(dst_dir, exist_ok=True)
    dst = os.path.join(dst_dir, SRC_NAME)
    nbytes = copy_checked(src, dst)
    print(f"copied {src} -> {dst} ({nbytes} bytes)")
    return 0


def _sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def copy_checked(src, dst):
    """Copy src to dst and confirm the copy is byte-identical."""
    shutil.copyfile(src, dst)
    if _sha256(src) != _sha256(dst):
        raise IOError(f"copy mismatch: {src} -> {dst}")
    return os.path.getsize(dst)


if __name__ == "__main__":
    raise SystemExit(main())
