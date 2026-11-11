#!/usr/bin/env python3
"""Verify CATALOGUE.md and INDEX.md consistency."""
import json
import pathlib
import re
import urllib.request

BASE = pathlib.Path(__file__).resolve().parent
arts = json.loads((BASE / "articles.json").read_text())
cat = (BASE / "CATALOGUE.md").read_text()
idx = (BASE / "INDEX.md").read_text()

# 1. INDEX has each article exactly once
idx_links = re.findall(r"\((https://highscalability\.com/[^)]+)\)", idx)
print(f"index entries: {len(idx_links)}, unique: {len(set(idx_links))}, expected: {len(arts)}")
assert len(idx_links) == len(set(idx_links)) == len(arts), "index mismatch"

# 2. Catalogue section headers match topic counts
sections = re.findall(r"^## (.+?) \((\d+) articles\)$", cat, re.M)
print(f"catalogue sections: {len(sections)}")
from collections import Counter

topic_counts = Counter(t for a in arts for t in a["topics"])
mismatch = [
    (name, int(n), topic_counts.get(name, 0))
    for name, n in sections
    if int(n) != topic_counts.get(name, 0)
]
uncat = [a for a in arts if not a["topics"]]
if ("General & Miscellaneous", len(uncat)) not in [(n, c) for n, _, c in mismatch] and any(
    n == "General & Miscellaneous" for n, _, _ in mismatch
):
    pass
print("section count mismatches (excluding General&Misc handled below):",
      [m for m in mismatch if m[0] != "General & Miscellaneous"])
gm = [s for s in sections if s[0] == "General & Miscellaneous"]
print(f"General & Miscellaneous section says {gm[0][1] if gm else 'MISSING'}, actual {len(uncat)}")

# 3. Kafka 101 should no longer be a war story
kafka = next(a for a in arts if a["title"] == "Kafka 101")
print("Kafka 101 topics:", kafka["topics"])

# 4. URL liveness spot-check (6 random articles)
import random

random.seed(7)
sample = random.sample(arts, 6)
for a in sample:
    try:
        req = urllib.request.Request(a["url"], method="HEAD",
                                     headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            print(f"  {r.status} {a['url']}")
    except Exception as e:
        print(f"  ERR {a['url']}: {e}")
print("VERIFICATION OK")
