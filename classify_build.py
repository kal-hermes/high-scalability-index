#!/usr/bin/env python3
"""Classify articles into topics (multi-label) and build CATALOGUE.md + INDEX.md."""
import json
import pathlib
import re
from collections import Counter

BASE = pathlib.Path(__file__).resolve().parent
articles = json.loads((BASE / "articles.json").read_text())

# Topic taxonomy: (topic name, regex applied to title + excerpt).
# Word boundaries are enforced by the matcher. An article may match many topics.
TOPICS: list[tuple[str, str]] = [
    ("Link Roundups", r"stuff the internet says"),
    ("Sponsored Posts", r"sponsored post"),
    ("Company Profiles & War Stories",
     r"\b(google|facebook|meta|netflix|amazon|aws|uber|twitter|linkedin|whatsapp|instagram|"
     r"youtube|airbnb|dropbox|slack|discord|reddit|pinterest|shopify|stripe|paypal|ebay|walmart|"
     r"spotify|tiktok|bytedance|cloudflare|tesla|apple|microsoft|alibaba|tencent|baidu|twilio|"
     r"github|stack overflow|stackoverflow|flickr|digg|tumblr|zynga| snapchat|telegram|discord|"
     r"mySpace|myspace|skype|x\.com|openai|anthropic|stripe|roblox|fortnite|riot|valve|steam)\b"),
    ("Distributed Systems Theory",
     r"\b(consensus|paxos|raft|gossip|CAP theorem|consistency model|quorum|vector clock|"
     r"distributed (system|systems|database|databases|computing|lock|locks|transaction)|"
     r"byzantine|two[- ]phase|CRDT|leader election|logical clock|lamport|distributed hash)\b"),
    ("Scalability Architecture & Patterns",
     r"\b(scal(e|es|ing|ability|able)|shard|shards|sharding|partitioning|horizontal scaling|"
     r"vertical scaling|replication|replicas?|eventual consistency|backpressure|"
     r"shared[- ]nothing|cell[- ]based architecture|capacity planning)\b"),
    ("Databases & SQL",
     r"\b(mysql|postgres|postgresql|sqlite|oracle db|sql server|mariadb|relational|"
     r"database|databases|indexing strategy|join|joins|transaction|transactions|schema|"
     r"stored procedure|N+1|connection pool)\b"),
    ("NoSQL & Key-Value Stores",
     r"\b(nosql|mongodb|mongo|cassandra|dynamodb|dynamo|couchbase|couchdb|hbase|bigtable|"
     r"neo4j|riak|voldemort|redis|memcached|key[- ]value|wide[- ]column|document store|"
     r"aerospike|scylladb|foundationdb)\b"),
    ("Caching & CDNs",
     r"\b(cache|caches|caching|cdn|content delivery network|varnish|edge computing|"
     r"cache invalidation|memoization|read replica)\b"),
    ("Messaging & Event Streaming",
     r"\b(kafka|rabbitmq|activemq|message (queue|queues|broker)|event[- ]driven|event sourcing|"
     r"streaming|kinesis|nats|pub/?sub|zeromq|sqs|sqs|pulsar|event loop|queue|queues|"
     r"ingest|ingestion)\b"),
    ("Microservices & APIs",
     r"\b(microservice|microservices|monolith|monolithic|service[- ]oriented|soa|rest|restful|"
     r"graphql|grpc|api gateway|service mesh|webhooks?|sidecar|service discovery|"
     r"backend[- ]for[- ]frontend|bff)\b"),
    ("Big Data & Analytics",
     r"\b(hadoop|spark|mapreduce|presto|trino|hive|data warehouse|data lake|etl|elt|"
     r"batch processing|big data|petabyte|exabyte|analytics|clickstream|olap|"
     r"apache airflow|dbt|snowflake|databricks)\b"),
    ("Search & Indexing",
     r"\b(elasticsearch|elastic search|solr|lucene|opensearch|search engine|inverted index|"
     r"full[- ]text search|searching at|ranking)\b"),
    ("Cloud Platforms & Serverless",
     r"\b(aws|amazon web services|ec2|s3|azure|google cloud|gcp|\bcloud\b|cloud computing|"
     r"lambda|serverless|faas|paas|iaas|multi[- ]cloud|hybrid cloud|cloud native|"
     r"cloudflare workers|digitalocean|linode|heroku)\b"),
    ("Containers & Orchestration",
     r"\b(kubernetes|k8s|docker|container|containers|containeriz|ecs|mesos|marathon|"
     r"orchestration|helm|istio|rkt|containerd|podman)\b"),
    ("Load Balancing & Traffic Management",
     r"\b(load balanc|haproxy|nginx|envoy|traffic management|rate limit|rate limiting|"
     r"throttl|reverse proxy|anycast|dns|round robin|failover routing|global traffic)\b"),
    ("Storage & Filesystems",
     r"\b(storage|ssd|hdd|hard drive|disk|disks|object storage|filesystem|hdfs|gluster|ceph|"
     r"raid|san|nas|block storage|nfs|zfs|storage engine)\b"),
    ("Performance & Latency",
     r"\b(latency|performance|throughput|optimization|optimisation|optimiz|benchmark|"
     r"tail latency|milliseconds|profiling|bottleneck|slow|speed|faster|p99|p95|qps|rps)\b"),
    ("Networking",
     r"\b(tcp|udp|http/?2|http/?3|quic|network|networks|networking|bgp|socket|sockets|"
     r"bandwidth|5g|ipv6|packet|congestion|subnet|vpn|tls|ssl)\b"),
    ("Hardware & Datacenters",
     r"\b(datacenter|data center|data centres?|server|servers|cpu|gpu|arm|power consumption|"
     r"cooling|rack|nvidia|intel|amd|chip|chips|silicon|fpga|memory bandwidth|dram|nvme)\b"),
    ("AI & Machine Learning",
     r"\b(machine learning|\bml\b|deep learning|neural|llm|llms|gpt|chatgpt|\bai\b|"
     r"artificial intelligence|recommendation|recommendations|model training|tensorflow|"
     r"pytorch|inference|embedding|rag\b|transformer)\b"),
    ("Security",
     r"\b(security|vulnerab|breach|breaches|encryption|ddos|authentication|authorization|"
     r"password|zero[- ]trust|cipher|hacking|hacker|attack|exploit|malware|phishing|"
     r"private key|secrets? management)\b"),
    ("Reliability, SRE & Operations",
     r"\b(outage|outages|downtime|\bsre\b|site reliability|incident|incidents|failover|"
     r"disaster recovery|high availability|resilience|resilient|redundancy|monitoring|"
     r"observability|alerting|on[- ]call|postmortem|post[- ]mortem| MTTR|error budget)\b"),
    ("Programming & Languages",
     r"\b(java|python|golang|\bgo\b|rust|c\+\+|javascript|node|node\.js|garbage collection|"
     r"concurrency|async|runtime|compiler|erlang|elixir|php|\.net|ruby|perl|scala|kotlin|"
     r"swift|programming|language|multi[- ]thread|thread|threads)\b"),
    ("Operating Systems & Virtualization",
     r"\b(linux|unix|kernel|virtualization|virtualisation|virtual machine|vm|hypervisor|"
     r"wasm|webassembly|operating system)\b"),
]

COMPILED = [(name, re.compile(pat, re.I)) for name, pat in TOPICS]
# Topics that only fire on the title (excerpt mentions are too noisy)
TITLE_ONLY = {"Company Profiles & War Stories"}


def classify(art: dict) -> list[str]:
    title = art["title"]
    text = f"{title} {art['excerpt']}"
    # Roundups and sponsored posts are link dumps/solicitations: classify only as themselves
    if re.search(r"stuff the internet says", title, re.I):
        return ["Link Roundups"]
    if re.search(r"sponsored post", title, re.I):
        return ["Sponsored Posts"]
    hits = [
        name
        for name, rx in COMPILED
        if rx.search(title if name in TITLE_ONLY else text)
    ]
    return hits


def main() -> None:
    for art in articles:
        art["topics"] = classify(art)

    uncategorized = [a for a in articles if not a["topics"]]
    print(f"total={len(articles)}, uncategorized={len(uncategorized)}")

    counts = Counter(t for a in articles for t in a["topics"])
    for name, _ in TOPICS:
        print(f"  {name}: {counts.get(name, 0)}")

    # ---- CATALOGUE.md (by topic, articles may repeat across topics) ----
    lines = [
        "# HighScalability.com — Article Catalogue by Topic",
        "",
        f"Generated from the site archive (pages 2–205). {len(articles)} unique articles.",
        "An article may appear under more than one topic. Titles link to the original article.",
        "",
    ]
    for name, _ in TOPICS:
        arts = [a for a in articles if name in a["topics"]]
        if not arts:
            continue
        arts.sort(key=lambda x: (x["date"], x["title"]), reverse=True)
        lines.append(f"## {name} ({len(arts)} articles)")
        lines.append("")
        for a in arts:
            author = f" — {a['author']}" if a["author"] else ""
            lines.append(f"- [{a['title']}]({a['url']}) ({a['date']}{author})")
        lines.append("")
    if uncategorized:
        lines.append(f"## General & Miscellaneous ({len(uncategorized)} articles)")
        lines.append("")
        for a in sorted(uncategorized, key=lambda x: x["date"], reverse=True):
            lines.append(f"- [{a['title']}]({a['url']}) ({a['date']})")
        lines.append("")
    (BASE / "CATALOGUE.md").write_text("\n".join(lines))

    # ---- INDEX.md (chronological master index) ----
    idx = [
        "# HighScalability.com — Master Article Index",
        "",
        f"All {len(articles)} unique articles, newest first. Page = archive page where first seen.",
        "",
    ]
    for a in sorted(articles, key=lambda x: (x["date"], x["title"]), reverse=True):
        topics = ", ".join(a["topics"]) if a["topics"] else "—"
        idx.append(
            f"- {a['date']} · [{a['title']}]({a['url']}) · topics: {topics} · p.{a['first_seen_page']}"
        )
    (BASE / "INDEX.md").write_text("\n".join(idx))

    # keep enriched data
    (BASE / "articles.json").write_text(json.dumps(articles, indent=1))
    print(f"\nCATALOGUE.md: {(BASE / 'CATALOGUE.md').stat().st_size} bytes")
    print(f"INDEX.md: {(BASE / 'INDEX.md').stat().st_size} bytes")


if __name__ == "__main__":
    main()
