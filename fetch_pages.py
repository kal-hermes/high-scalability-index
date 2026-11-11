#!/usr/bin/env python3
"""Fetch highscalability.com archive pages 2..205 (resumable)."""
import concurrent.futures as cf
import pathlib
import random
import sys
import time
import urllib.request

BASE = pathlib.Path(__file__).resolve().parent
PAGES = BASE / "pages"
PAGES.mkdir(exist_ok=True)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


def fetch(n: int) -> tuple[int, str]:
    dest = PAGES / f"page{n:03d}.html"
    if dest.exists() and dest.stat().st_size > 5000:
        return n, "cached"
    url = f"https://highscalability.com/page/{n}/"
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
            dest.write_bytes(data)
            return n, f"ok {len(data)}"
        except Exception as e:
            if attempt == 3:
                return n, f"FAIL {e}"
            time.sleep(1.5 * (attempt + 1) + random.random())
    return n, "FAIL unreachable"


def main() -> None:
    lo, hi = 2, 205
    todo = list(range(lo, hi + 1))
    fails: list[tuple[int, str]] = []
    done = 0
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        for n, status in ex.map(fetch, todo):
            done += 1
            if status.startswith("FAIL"):
                fails.append((n, status))
            if done % 25 == 0 or status.startswith("FAIL"):
                print(f"[{done}/{len(todo)}] page {n}: {status}", flush=True)
    print(f"\nDone. {len(todo) - len(fails)} ok/cached, {len(fails)} failed")
    for n, s in fails:
        print(f"  page {n}: {s}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
