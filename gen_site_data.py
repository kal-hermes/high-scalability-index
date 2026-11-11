#!/usr/bin/env python3
"""Generate site/data/articles.js (script-tag-loadable, works on file:// and http)."""
import json
import pathlib
import re

BASE = pathlib.Path(__file__).resolve().parent
arts = json.loads((BASE / "articles_v2.json").read_text())

CONTENT_TYPES = {"Link Roundups", "Sponsored Posts", "Papers, Books & Research"}


def slug(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[&,]+", " ", s)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return re.sub(r"-+", "-", s)


TOPIC_ORDER = [
    "Scalability Architecture & Patterns", "Distributed Systems Theory",
    "Databases & SQL", "NoSQL & Key-Value Stores", "Caching & In-Memory Data Grids",
    "CDNs & Content Delivery", "Messaging & Event Streaming", "Microservices & APIs",
    "Big Data & Analytics", "Search & Indexing", "Cloud Platforms & Serverless",
    "Containers & Orchestration", "Load Balancing & Traffic Management",
    "Storage & Filesystems", "Performance & Latency", "Networking",
    "Hardware & Datacenters", "AI & Machine Learning", "Security",
    "Reliability, SRE & Operations", "Programming & Languages",
    "Operating Systems & Virtualization", "Company Profiles & War Stories",
    "Papers, Books & Research", "Link Roundups", "Sponsored Posts",
]

counts: dict[str, int] = {}
years = set()
out_arts = []
for a in arts:
    topics = a["topics"] if a["topics"] else ["General & Miscellaneous"]
    for t in topics:
        counts[t] = counts.get(t, 0) + 1
    if a["date"]:
        years.add(a["date"][:4])
    out_arts.append({
        "u": a["url"],
        "t": a["title"],
        "d": a["date"],
        "a": a["author"].replace("By ", "") if a["author"] else "",
        "tp": [slug(t) for t in topics],
        "x": (a["excerpt"][:220] + "…") if len(a["excerpt"]) > 220 else a["excerpt"],
    })

out_topics = []
for t in TOPIC_ORDER + ["General & Miscellaneous"]:
    if counts.get(t):
        out_topics.append({
            "slug": slug(t),
            "name": t,
            "count": counts[t],
            "kind": "content" if t in CONTENT_TYPES else "subject",
        })

data = {
    "generated": "2026-11-10",
    "source": "highscalability.com archive, pages 2-205",
    "topics": out_topics,
    "years": sorted(years),
    "articles": out_arts,
}
out = BASE / "site" / "data" / "articles.js"
out.write_text("window.HSDATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n")
print(f"articles: {len(out_arts)}, topics: {len(out_topics)}, size: {out.stat().st_size} bytes")
