#!/usr/bin/env python3
"""Extract official tags + main text from every fetched article -> article_text/."""
import concurrent.futures as cf
import hashlib
import html as htmllib
import json
import pathlib
import re

BASE = pathlib.Path(__file__).resolve().parent
SRC = BASE / "articles_html"
OUT = BASE / "article_text"
OUT.mkdir(exist_ok=True)

TAG_RE = re.compile(r'<meta property="article:tag" content="([^"]*)">')
TITLE_RE = re.compile(r'<title>(.*?)</title>', re.S)
CONTENT_RE = re.compile(r'<section class="gh-content[^"]*">(.*?)</section>', re.S)
STRIP = [
    re.compile(r'<script.*?</script>', re.S),
    re.compile(r'<style.*?</style>', re.S),
    re.compile(r"<!--.*?-->", re.S),
]


def extract(path: pathlib.Path) -> dict | None:
    html = path.read_text(errors="replace")
    tags = sorted({htmllib.unescape(t).strip() for t in TAG_RE.findall(html) if t.strip()})
    m = CONTENT_RE.search(html)
    body = m.group(1) if m else ""
    for rx in STRIP:
        body = rx.sub("", body)
    body = re.sub(r"<(h[1-6]|p|li|blockquote|pre|figcaption|tr)[^>]*>", "\n", body)
    text = re.sub(r"<[^>]+>", " ", body)
    text = htmllib.unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text).strip()
    t = TITLE_RE.search(html)
    title = htmllib.unescape(t.group(1)).strip() if t else ""
    return {"tags": tags, "text": text, "page_title": title}


def work(k: str) -> str:
    out = OUT / f"{k}.txt"
    if out.exists():
        return "cached"
    r = extract(SRC / f"{k}.html")
    if r is None:
        return "nohtml"
    out.write_text(json.dumps(r, ensure_ascii=False))
    return "ok"


def main() -> None:
    keys = [p.stem for p in SRC.glob("*.html")]
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        stats = list(ex.map(work, keys))
    from collections import Counter

    print(Counter(stats), "of", len(keys))
    # tag vocabulary stats
    tag_counter: Counter[str] = Counter()
    empty_text = 0
    for p in OUT.glob("*.txt"):
        d = json.loads(p.read_text())
        tag_counter.update(d["tags"])
        if len(d["text"]) < 200:
            empty_text += 1
    print(f"distinct tags: {len(tag_counter)}, articles with <200 chars text: {empty_text}")
    print("top 40 tags:")
    for tag, n in tag_counter.most_common(40):
        print(f"  {n:5d}  {tag}")


if __name__ == "__main__":
    main()
