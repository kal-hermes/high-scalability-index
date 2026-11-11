#!/usr/bin/env python3
"""Rebuild CATALOGUE.md + INDEX.md from articles_v2.json (v2, full-text verified)."""
import json
import pathlib

BASE = pathlib.Path(__file__).resolve().parent
arts = json.loads((BASE / "articles_v2.json").read_text())

ORDER = [
    "Link Roundups", "Sponsored Posts", "Company Profiles & War Stories",
    "Papers, Books & Research", "Scalability Architecture & Patterns",
    "Distributed Systems Theory", "Databases & SQL", "NoSQL & Key-Value Stores",
    "Caching & In-Memory Data Grids", "CDNs & Content Delivery",
    "Messaging & Event Streaming", "Microservices & APIs", "Big Data & Analytics",
    "Search & Indexing", "Cloud Platforms & Serverless", "Containers & Orchestration",
    "Load Balancing & Traffic Management", "Storage & Filesystems",
    "Performance & Latency", "Networking", "Hardware & Datacenters",
    "AI & Machine Learning", "Security", "Reliability, SRE & Operations",
    "Programming & Languages", "Operating Systems & Virtualization",
]

uncategorized = [a for a in arts if not a["topics"]]

lines = [
    "# HighScalability.com — Article Catalogue by Topic (v2)",
    "",
    f"{len(arts)} unique articles from the site archive (pages 2–205).",
    "v2: every article was fetched and classified against its FULL TEXT and the site's own",
    "editorial tags — not just title/excerpt. An article may appear under multiple topics.",
    "",
]
for name in ORDER:
    subset = sorted(
        (a for a in arts if name in a["topics"]),
        key=lambda x: (x["date"], x["title"]), reverse=True,
    )
    if not subset:
        continue
    lines.append(f"## {name} ({len(subset)} articles)")
    lines.append("")
    for a in subset:
        author = f" — {a['author']}" if a["author"] else ""
        lines.append(f"- [{a['title']}]({a['url']}) ({a['date']}{author})")
    lines.append("")
lines.append(f"## General & Miscellaneous ({len(uncategorized)} articles)")
lines.append("")
for a in sorted(uncategorized, key=lambda x: (x["date"], x["title"]), reverse=True):
    lines.append(f"- [{a['title']}]({a['url']}) ({a['date']})")
lines.append("")
(BASE / "CATALOGUE.md").write_text("\n".join(lines))

idx = [
    "# HighScalability.com — Master Article Index (v2)",
    "",
    f"All {len(arts)} unique articles, newest first. p.N = archive page where first seen.",
    "topics are v2 (verified against full text + site editorial tags); tags = site's own.",
    "",
]
for a in sorted(arts, key=lambda x: (x["date"], x["title"]), reverse=True):
    topics = ", ".join(a["topics"]) if a["topics"] else "—"
    tags = "; ".join(a["site_tags"][:6])
    tag_part = f" · tags: {tags}" if tags else ""
    idx.append(
        f"- {a['date']} · [{a['title']}]({a['url']}) · topics: {topics} · p.{a['first_seen_page']}{tag_part}"
    )
(BASE / "INDEX.md").write_text("\n".join(idx))

print(f"CATALOGUE.md: {(BASE / 'CATALOGUE.md').stat().st_size} bytes")
print(f"INDEX.md: {(BASE / 'INDEX.md').stat().st_size} bytes")
print(f"total={len(arts)} uncategorized={len(uncategorized)}")
