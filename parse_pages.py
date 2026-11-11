#!/usr/bin/env python3
"""Parse downloaded archive pages into articles.json (dedup across pages)."""
import html as htmllib
import json
import pathlib
import re

BASE = pathlib.Path(__file__).resolve().parent
PAGES = BASE / "pages"

ART_RE = re.compile(r'<article class="gh-card[^"]*">(.*?)</article>', re.S)
HREF_RE = re.compile(r'<a class="gh-card-link" href="([^"]+)"')
TITLE_RE = re.compile(r'<h3 class="gh-card-title[^"]*">(.*?)</h3>', re.S)
EXCERPT_RE = re.compile(r'<p class="gh-card-excerpt[^"]*">(.*?)</p>', re.S)
AUTHOR_RE = re.compile(r'<span class="gh-card-author">(.*?)</span>', re.S)
DATE_RE = re.compile(r'<time class="gh-card-date" datetime="([^"]+)"')


def strip_tags(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    s = htmllib.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def main() -> None:
    articles: dict[str, dict] = {}
    for f in sorted(PAGES.glob("page*.html")):
        page_no = int(f.stem.replace("page", ""))
        text = f.read_text(errors="replace")
        for art in ART_RE.findall(text):
            m = HREF_RE.search(art)
            if not m:
                continue
            href = m.group(1)
            url = href if href.startswith("http") else f"https://highscalability.com{href}"
            t = TITLE_RE.search(art)
            e = EXCERPT_RE.search(art)
            a = AUTHOR_RE.search(art)
            d = DATE_RE.search(art)
            title = strip_tags(t.group(1)) if t else ""
            if url in articles:
                continue
            articles[url] = {
                "url": url,
                "title": title,
                "excerpt": strip_tags(e.group(1)) if e else "",
                "author": strip_tags(a.group(1)) if a else "",
                "date": d.group(1) if d else "",
                "first_seen_page": page_no,
            }
    out = sorted(articles.values(), key=lambda x: (x["date"], x["title"]), reverse=True)
    (BASE / "articles.json").write_text(json.dumps(out, indent=1))
    print(f"{len(out)} unique articles from {len(list(PAGES.glob('page*.html')))} pages")
    no_title = sum(1 for x in out if not x["title"])
    no_date = sum(1 for x in out if not x["date"])
    print(f"missing title: {no_title}, missing date: {no_date}")


if __name__ == "__main__":
    main()
