#!/usr/bin/env python3
"""Emit site/data.js from articles_v2.json (the UI's single data source)."""
import json
import pathlib
import re

BASE = pathlib.Path(__file__).resolve().parent.parent
arts = json.loads((BASE / "articles_v2.json").read_text())

SLUGS = {
    "Link Roundups": "link-roundups",
    "Sponsored Posts": "sponsored-posts",
    "Company Profiles & War Stories": "war-stories",
    "Papers, Books & Research": "papers-books-research",
    "Scalability Architecture & Patterns": "scalability-architecture-patterns",
    "Distributed Systems Theory": "distributed-systems-theory",
    "Databases & SQL": "databases-sql",
    "NoSQL & Key-Value Stores": "nosql-key-value-stores",
    "Caching & In-Memory Data Grids": "caching-in-memory-data-grids",
    "CDNs & Content Delivery": "cdns-content-delivery",
    "Messaging & Event Streaming": "messaging-event-streaming",
    "Microservices & APIs": "microservices-apis",
    "Big Data & Analytics": "big-data-analytics",
    "Search & Indexing": "search-indexing",
    "Cloud Platforms & Serverless": "cloud-platforms-serverless",
    "Containers & Orchestration": "containers-orchestration",
    "Load Balancing & Traffic Management": "load-balancing-traffic-management",
    "Storage & Filesystems": "storage-filesystems",
    "Performance & Latency": "performance-latency",
    "Networking": "networking",
    "Hardware & Datacenters": "hardware-datacenters",
    "AI & Machine Learning": "ai-machine-learning",
    "Security": "security",
    "Reliability, SRE & Operations": "reliability-sre-operations",
    "Programming & Languages": "programming-languages",
    "Operating Systems & Virtualization": "operating-systems-virtualization",
    "General & Miscellaneous": "general-miscellaneous",
}
TOPIC_ORDER = list(SLUGS.keys())
CONTENT_BUCKETS = {"Link Roundups", "Sponsored Posts"}

counts = {t: 0 for t in TOPIC_ORDER}
for a in arts:
    for t in a["topics"]:
        counts[t] += 1
for a in arts:
    if not a["topics"]:
        counts["General & Miscellaneous"] += 1

def slug(t): return SLUGS[t]

def author(a):
    return re.sub(r"^By\s+", "", a["author"]) if a["author"] else "High Scalability"

def excerpt(a):
    e = (a.get("excerpt") or "").strip()
    return (e[:220] + "…") if len(e) > 220 else e

articles_out = []
for a in arts:
    topics = a["topics"] or ["General & Miscellaneous"]
    articles_out.append({
        "u": a["url"],
        "t": a["title"],
        "d": a["date"],
        "a": author(a),
        "e": excerpt(a),
        "tp": [SLUGS[t] for t in topics if t in SLUGS],
    })

technical = [t for t in TOPIC_ORDER if t not in CONTENT_BUCKETS and counts[t] > 0]
buckets = [t for t in TOPIC_ORDER if t in CONTENT_BUCKETS and counts[t] > 0]
technical.sort(key=lambda t: -counts[t])
buckets.sort(key=lambda t: -counts[t])

data = {
    "generated": "2026-11-10",
    "source": "articles_v2.json (full-text + site-tag verified classification)",
    "topics": [
        {"slug": slug(t), "name": t, "count": counts[t], "bucket": t in CONTENT_BUCKETS}
        for t in technical + buckets
    ],
    "articles": articles_out,
}
out = "window.HS_DATA=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";"
(BASE / "site" / "data.js").write_text(out)
print(f"data.js written: {len(out)} bytes, {len(articles_out)} articles, {len(data['topics'])} topics")
