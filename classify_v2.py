#!/usr/bin/env python3
"""Classify v2: verified against full article text + official editorial tags.

Topic membership rule (per article, per topic):
  - Link Roundups / Sponsored Posts: title match OR official tag (early return)
  - otherwise topic is assigned if ANY of:
      a) an official editorial tag maps to it            (site's own judgment)
      b) a topic keyword matches the title               (v1 signal, strong)
      c) topic has >=3 DISTINCT keyword hits in full text, or >=2 distinct
         hits with one keyword appearing >=5 times       (substantive coverage)
  - Company topic additionally allows an entity tag or a single company
    name appearing >=8 times in the text (war-story depth).
Writes articles_v2.json + classification_changes.json, rebuilds outputs.
"""
import json
import pathlib
import re
from collections import Counter

BASE = pathlib.Path(__file__).resolve().parent
META_TAGS = {  # content-type / editorial meta tags -> not topics
    "strategy", "example", "general discussion", "product", "wisdom", "interesting",
    "perspectives", "humor", "funny", "joke", "future", "high-scalability", "blog",
    "web", "software", "data", "application", "web application", "website", "design",
    "blueprint", "framework", "tutorial", "teaching", "startup", "jobs", "conference",
    "problem", "problems", "admin", "administrator", "administration", "ambient",
    "activ8", "best platform", "enterprise", "sessions", "video", "mobile", "graph",
    "real-time", "open source", "drupal", "web 2.0", "enterprise architecture",
    "programming model", "askhighscalability", "language", "management", "software",
    "games", "cheap", "diy", "television", "social network", "social networking",
    "scalability secrets", "virtualization?", "image server", "space-based architecture",
}

ROUNDUP = "Link Roundups"
SPONSORED = "Sponsored Posts"
COMPANY = "Company Profiles & War Stories"
PAPERS = "Papers, Books & Research"
CDN = "CDNs & Content Delivery"
CACHING = "Caching & In-Memory Data Grids"

TAG_MAP: dict[str, list[str]] = {
    "hot links": [ROUNDUP], "sponsored post": [SPONSORED],
    "paper": [PAPERS], "papers": [PAPERS], "book": [PAPERS],
    # databases
    "mysql": ["Databases & SQL"], "database": ["Databases & SQL"],
    "databases": ["Databases & SQL"], "rdbms": ["Databases & SQL"], "sql": ["Databases & SQL"],
    "mysql cluster": ["Databases & SQL"], "mysql load": ["Databases & SQL"],
    "mysql-proxy": ["Databases & SQL"], "sql server 2008": ["Databases & SQL"],
    "postgres": ["Databases & SQL"], "postgresql": ["Databases & SQL"],
    "oracle": ["Databases & SQL"], "jdbc": ["Databases & SQL"],
    "database replication": ["Databases & SQL", "Scalability Architecture & Patterns"],
    "database scalability": ["Databases & SQL", "Scalability Architecture & Patterns"],
    "database-as-a-service": ["Databases & SQL", "Cloud Platforms & Serverless"],
    "connection-pool": ["Databases & SQL"], "hibernate": ["Databases & SQL"],
    "database performance online website": ["Databases & SQL"],
    "analytics large database real time": ["Databases & SQL", "Big Data & Analytics"],
    # nosql
    "nosql": ["NoSQL & Key-Value Stores"], "key-value store": ["NoSQL & Key-Value Stores"],
    "bigtable": ["NoSQL & Key-Value Stores"], "mongodb": ["NoSQL & Key-Value Stores"],
    "cassandra": ["NoSQL & Key-Value Stores"], "hbase": ["NoSQL & Key-Value Stores"],
    "couchdb": ["NoSQL & Key-Value Stores"], "simpledb": ["NoSQL & Key-Value Stores"],
    "dht": ["NoSQL & Key-Value Stores", "Distributed Systems Theory"],
    # caching / data grids / cdn
    "cache": [CACHING], "caching": [CACHING], "memcached": [CACHING], "memcache": [CACHING],
    "redis": [CACHING], "redis cluster": [CACHING], "varnish": [CACHING], "squid": [CACHING],
    "distributed caching": [CACHING], "distribucted caching": [CACHING],
    "in-memory": [CACHING], "memory-grid": [CACHING], "datagrid": [CACHING],
    "data-grid": [CACHING], "imdg": [CACHING], "coherence": [CACHING],
    "gigaspaces": [CACHING], "gigaspaeces": [CACHING],
    "cdn": [CDN], "content delivery": [CDN], "content delivery network": [CDN],
    # scalability patterns
    "scalability": ["Scalability Architecture & Patterns"], "scalable": ["Scalability Architecture & Patterns"],
    "scaling": ["Scalability Architecture & Patterns"], "scalabilty": ["Scalability Architecture & Patterns"],
    "scalabitliy": ["Scalability Architecture & Patterns"],
    "shard": ["Scalability Architecture & Patterns"], "shards": ["Scalability Architecture & Patterns"],
    "sharding": ["Scalability Architecture & Patterns"], "partitioning": ["Scalability Architecture & Patterns"],
    "horizontal scaling": ["Scalability Architecture & Patterns"],
    "horizontal scalability": ["Scalability Architecture & Patterns"],
    "diagonal scaling": ["Scalability Architecture & Patterns"],
    "vertical scaling": ["Scalability Architecture & Patterns"], "scale-out": ["Scalability Architecture & Patterns"],
    "consistent hashing": ["Scalability Architecture & Patterns"],
    "architecture partitioning scaling": ["Scalability Architecture & Patterns"],
    "replication": ["Scalability Architecture & Patterns"],
    "master-slave": ["Scalability Architecture & Patterns"],
    # distributed systems
    "distributed": ["Distributed Systems Theory"], "distirbuted": ["Distributed Systems Theory"],
    "distributed systems": ["Distributed Systems Theory"],
    "distributed computing": ["Distributed Systems Theory"],
    "distributed storage": ["Distributed Systems Theory", "Storage & Filesystems"],
    "cluster": ["Distributed Systems Theory"], "clusters": ["Distributed Systems Theory"],
    "clustering": ["Distributed Systems Theory"], "grid": ["Big Data & Analytics"],
    "geo-distributed clusters": ["Distributed Systems Theory"],
    "cap": ["Distributed Systems Theory"], "paxos": ["Distributed Systems Theory"],
    "consistentcy": ["Distributed Systems Theory"], "fault-tolerance": ["Reliability, SRE & Operations"],
    "failure": ["Reliability, SRE & Operations"], "failure analysis": ["Reliability, SRE & Operations"],
    # big data
    "hadoop": ["Big Data & Analytics"], "mapreduce": ["Big Data & Analytics"],
    "map reduce": ["Big Data & Analytics"], "bigdata": ["Big Data & Analytics"],
    "big-data": ["Big Data & Analytics"], "hpc": ["Big Data & Analytics"],
    "hive": ["Big Data & Analytics"], "cloudera": ["Big Data & Analytics"],
    "analytics": ["Big Data & Analytics"], "data management": ["Big Data & Analytics"],
    "job scheduling": ["Big Data & Analytics"], "log analyzer": ["Big Data & Analytics"],
    # cloud
    "cloud": ["Cloud Platforms & Serverless"], "cloud computing": ["Cloud Platforms & Serverless"],
    "public cloud": ["Cloud Platforms & Serverless"], "private cloud": ["Cloud Platforms & Serverless"],
    "hybrid": ["Cloud Platforms & Serverless"], "utility computing": ["Cloud Platforms & Serverless"],
    "aws": ["Cloud Platforms & Serverless"], "amazon": ["Cloud Platforms & Serverless"],
    "ec2": ["Cloud Platforms & Serverless"], "s3": ["Cloud Platforms & Serverless", "Storage & Filesystems"],
    "amazon s3": ["Cloud Platforms & Serverless", "Storage & Filesystems"],
    "gae": ["Cloud Platforms & Serverless"], "gce": ["Cloud Platforms & Serverless"],
    "azure": ["Cloud Platforms & Serverless"], "paas": ["Cloud Platforms & Serverless"],
    "saas": ["Cloud Platforms & Serverless"], "cloud deployment": ["Cloud Platforms & Serverless"],
    "cloud storage": ["Cloud Platforms & Serverless", "Storage & Filesystems"],
    "hosting": ["Cloud Platforms & Serverless"], "serverless": ["Cloud Platforms & Serverless"],
    "virtualization": ["Operating Systems & Virtualization"],
    # containers
    "docker": ["Containers & Orchestration"], "containers": ["Containers & Orchestration"],
    # load balancing / web servers
    "load balancing": ["Load Balancing & Traffic Management"],
    "load balancer": ["Load Balancing & Traffic Management"], "load balance": ["Load Balancing & Traffic Management"],
    "haproxy": ["Load Balancing & Traffic Management"], "nginx": ["Load Balancing & Traffic Management"],
    "lighttpd": ["Load Balancing & Traffic Management"], "web server": ["Load Balancing & Traffic Management"],
    "dns": ["Load Balancing & Traffic Management"],
    # storage
    "storage": ["Storage & Filesystems"], "ssd": ["Storage & Filesystems", "Hardware & Datacenters"],
    "file system": ["Storage & Filesystems"], "cluster file system": ["Storage & Filesystems"],
    "clustered storage system": ["Storage & Filesystems"], "cluster storage system": ["Storage & Filesystems"],
    "scaling storage": ["Storage & Filesystems"], "drbd": ["Storage & Filesystems"],
    # performance
    "performance": ["Performance & Latency"], "latency": ["Performance & Latency"],
    "benchmark": ["Performance & Latency"], "optimization": ["Performance & Latency"],
    "high performance": ["Performance & Latency"], "profiling": ["Performance & Latency"],
    "acceleration": ["Performance & Latency"],
    # security / ops
    "security": ["Security"], "devops": ["Reliability, SRE & Operations"],
    "deployment": ["Reliability, SRE & Operations"], "operations": ["Reliability, SRE & Operations"],
    "monitoring": ["Reliability, SRE & Operations"], "appliction monitoring": ["Reliability, SRE & Operations"],
    "automation": ["Reliability, SRE & Operations"], "testing": ["Reliability, SRE & Operations"],
    "logging": ["Reliability, SRE & Operations"],
    "high availability": ["Reliability, SRE & Operations", "Scalability Architecture & Patterns"],
    "high availablilty": ["Reliability, SRE & Operations", "Scalability Architecture & Patterns"],
    # languages
    "java": ["Programming & Languages"], "j2ee": ["Programming & Languages"],
    "python": ["Programming & Languages"], "php": ["Programming & Languages"],
    "ror": ["Programming & Languages"], "ruby": ["Programming & Languages"],
    "rails": ["Programming & Languages"], "perl": ["Programming & Languages"],
    "javascript": ["Programming & Languages"], "c++": ["Programming & Languages"],
    ".net": ["Programming & Languages"], "scala": ["Programming & Languages"],
    "erlang": ["Programming & Languages"], "django": ["Programming & Languages"],
    "lamp": ["Programming & Languages"], "ajax": ["Programming & Languages"],
    "mongrel": ["Programming & Languages"], "multithreading": ["Programming & Languages"],
    "parallelism": ["Programming & Languages"], "parallel": ["Programming & Languages"],
    "multicore": ["Hardware & Datacenters", "Programming & Languages"],
    # OS
    "linux": ["Operating Systems & Virtualization"], "windows": ["Operating Systems & Virtualization"],
    "solaris": ["Operating Systems & Virtualization"],
    # networking / messaging
    "networking": ["Networking"], "network": ["Networking"], "p2p": ["Networking"],
    "xmpp": ["Messaging & Event Streaming"], "queue": ["Messaging & Event Streaming"],
    "activemq": ["Messaging & Event Streaming"], "streaming": ["Messaging & Event Streaming"],
    # search / microservices
    "search": ["Search & Indexing"], "lucene": ["Search & Indexing"],
    "microservices": ["Microservices & APIs"], "api": ["Microservices & APIs"],
    # hardware / datacenter
    "hardware": ["Hardware & Datacenters"], "data center": ["Hardware & Datacenters"],
    "datacenter": ["Hardware & Datacenters"], "servers": ["Hardware & Datacenters"],
    "server": ["Hardware & Datacenters"],
    # company entity tags
    "google": [COMPANY], "facebook": [COMPANY], "netflix": [COMPANY], "twitter": [COMPANY],
    "yahoo": [COMPANY], "flickr": [COMPANY], "ibm": [COMPANY], "microsoft": [COMPANY],
    "eharmony": [COMPANY], "sun": [COMPANY], "joost": [COMPANY], "sun microsystems": [COMPANY],
}

KW: dict[str, list[str]] = {
    "Distributed Systems Theory": [
        "consensus", "paxos", "raft\\b", "gossip", "CAP theorem", "quorum", "vector clock",
        "byzantine", "two-phase", "CRDT", "leader election", "logical clock", "lamport",
        "distributed (system|systems|hash|transaction|lock|computing)", "eventual consistenc",
    ],
    "Scalability Architecture & Patterns": [
        "scal(e|es|ing|ability|able)\\b", "shard(ing|s|ed)?\\b", "partition(ing|ed|s)?\\b",
        "horizontal scal", "vertical scal", "replicat", "backpressure",
        "shared[- ]nothing", "capacity planning", "consistent hashing", "scale[- ]out",
        "cell[- ]based arch",
    ],
    "Databases & SQL": [
        "mysql", "postgres", "sqlite", "sql server", "mariadb", "\\bjoin\\b|joins\\b",
        "\\bN\\+1\\b", "stored procedure", "schema (migration|design)", "connection pool",
        "\\bindex(ing|es)?\\b.*\\b(query|database|sql|table)", "relational",
    ],
    "NoSQL & Key-Value Stores": [
        "nosql", "mongodb", "cassandra", "dynamodb", "couchbase", "hbase", "bigtable",
        "neo4j", "riak", "voldemort", "aerospike", "scylladb", "foundationdb",
        "key[- ]value", "wide[- ]column", "document (store|database|model)",
    ],
    CACHING: [
        "memcached", "redis", "varnish", "squid", "cache (hit|miss|invalidat|layer|tier|cluster)",
        "caching", "data ?grid", "in-memory data", "gigaspaces", "coherence", "imdg",
    ],
    CDN: [
        "\\bcdn\\b", "content delivery network", "edge (cache|location|network|server)",
        "akamai", "cloudflare", "fastly",
    ],
    "Messaging & Event Streaming": [
        "kafka", "rabbitmq", "activemq", "message (queue|broker)", "event[- ]driven",
        "event sourcing", "kinesis", "\\bnats\\b", "pub/?sub", "zeromq", "\\bsqs\\b",
        "pulsar", "ingest(ion)?\\b",
    ],
    "Microservices & APIs": [
        "microservice", "monolith", "service[- ]oriented", "\\bsoa\\b", "\\brest\\b|restful",
        "graphql", "grpc", "api gateway", "service mesh", "sidecar", "service discovery",
    ],
    "Big Data & Analytics": [
        "hadoop", "spark", "mapreduce", "presto", "trino", "hive", "data warehouse",
        "data lake", "\\betl\\b", "batch process", "big data", "petabyte", "olap",
        "airflow", "snowflake", "databricks", "clickstream",
    ],
    "Search & Indexing": [
        "elasticsearch", "opensearch", "solr", "lucene", "inverted index",
        "full[- ]text search", "search (engine|cluster|index|ranking|relevance)",
    ],
    "Cloud Platforms & Serverless": [
        "\\baws\\b", "amazon web services", "\\bec2\\b", "\\bs3\\b", "azure", "google cloud",
        "\\bgcp\\b", "\\blambda\\b", "serverless", "\\bpaas\\b", "\\biaas\\b",
        "multi[- ]cloud", "cloud native",
    ],
    "Containers & Orchestration": [
        "kubernetes", "\\bk8s\\b", "docker", "container", "ecs\\b", "mesos", "helm",
        "istio", "containerd", "podman",
    ],
    "Load Balancing & Traffic Management": [
        "load balan", "haproxy", "nginx", "envoy", "rate limit", "throttl",
        "reverse proxy", "anycast", "traffic (management|routing|shifting)",
    ],
    "Storage & Filesystems": [
        "\\bssd\\b", "\\bhdd\\b", "object storage", "filesystem", "hdfs", "ceph",
        "\\braid\\b", "block storage", "\\bnfs\\b", "zfs", "storage (engine|system|cluster|node)",
    ],
    "Performance & Latency": [
        "latency", "throughput", "benchmark", "tail latency", "\\bp99\\b|\\bp95\\b",
        "profil(ing|e)\\b", "bottleneck", "\\bqps\\b|\\brps\\b", "response time",
        "millisecond",
    ],
    "Networking": [
        "\\btcp\\b", "\\budp\\b", "http/?[23]", "\\bquic\\b", "\\bbgp\\b", "socket",
        "bandwidth", "\\b5g\\b", "ipv6", "packet", "congestion", "\\btls\\b|\\bssl\\b",
    ],
    "Hardware & Datacenters": [
        "data ?cent(er|re)s?\\b", "\\bcpu\\b", "\\bgpu\\b", "\\barm\\b", "power consumption",
        "cooling", "\\brack\\b", "nvidia", "\\bintel\\b", "\\bfpga\\b", "\\b dram\\b", "nvme",
        "multicore",
    ],
    "AI & Machine Learning": [
        "machine learning", "deep learning", "neural", "\\bllm\\b|\\bllms\\b", "\\bgpt\\b",
        "chatgpt", "artificial intelligence", "recommendation (engine|system|model)",
        "tensorflow", "pytorch", "model training", "inference", "embedding",
    ],
    "Security": [
        "vulnerab", "breach", "encryption", "\\bddos\\b", "authentication", "authorization",
        "\\bzero[- ]trust\\b", "cipher", "exploit", "malware", "phishing",
        "secrets? management", "\\btls\\b|\\bssl\\b",
    ],
    "Reliability, SRE & Operations": [
        "outage", "downtime", "\\bsre\\b", "site reliability", "incident",
        "disaster recovery", "high availability", "resilien", "redundan",
        "observability", "alerting", "on[- ]call", "post[- ]?mortem", "error budget",
        "failover",
    ],
    "Programming & Languages": [
        "\\bjava\\b", "\\bpython\\b", "\\bgolang\\b|\\bgo lang", "\\brust\\b", "c\\+\\+",
        "javascript", "node\\.js|\\bnode\\b", "garbage collection", "concurrency",
        "\\berlang\\b", "\\belixir\\b", "\\bphp\\b", "\\.net\\b", "\\bruby\\b", "\\bscala\\b",
        "multithread", "compiler", "runtime",
    ],
    "Operating Systems & Virtualization": [
        "linux", "unix", "kernel", "virtuali[sz]ation", "virtual machine", "hypervisor",
        "webassembly|\\bwasm\\b", "operating system",
    ],
    COMPANY: [
        "google", "facebook", "netflix", "amazon", "uber", "twitter", "linkedin",
        "whatsapp", "instagram", "youtube", "airbnb", "dropbox", "slack", "discord",
        "reddit", "pinterest", "shopify", "stripe", "paypal", "ebay", "spotify",
        "tiktok", "bytedance", "cloudflare", "tesla", "apple", "microsoft", "alibaba",
        "tencent", "baidu", "github", "stackoverflow|stack overflow", "flickr",
        "myspace", "telegram", "openai", "roblox", "duckduckgo",
    ],
    PAPERS: [],  # tag/title driven only
}

KWX = {t: [re.compile(p, re.I) for p in pats] for t, pats in KW.items()}
COMPANY_COUNT_MIN = 8
DISTINCT_MIN = 4
STRONG_OCCURRENCES = 5

TOPIC_ORDER = [
    ROUNDUP, SPONSORED, COMPANY, PAPERS,
    "Scalability Architecture & Patterns", "Distributed Systems Theory",
    "Databases & SQL", "NoSQL & Key-Value Stores", CACHING, CDN,
    "Messaging & Event Streaming", "Microservices & APIs", "Big Data & Analytics",
    "Search & Indexing", "Cloud Platforms & Serverless", "Containers & Orchestration",
    "Load Balancing & Traffic Management", "Storage & Filesystems",
    "Performance & Latency", "Networking", "Hardware & Datacenters",
    "AI & Machine Learning", "Security", "Reliability, SRE & Operations",
    "Programming & Languages", "Operating Systems & Virtualization",
]


def norm_tag(t: str) -> str:
    return re.sub(r"\s+", " ", t.strip().lower())


def classify(art: dict, tags: list[str], text: str) -> list[str]:
    title = art["title"]
    ntags = {norm_tag(t) for t in tags}
    # early returns
    if "stuff the internet says" in title.lower() or "hot links" in ntags:
        return [ROUNDUP]
    if "sponsored post" in title.lower() or "sponsored post" in ntags:
        return [SPONSORED]
    topics: set[str] = set()
    evidence: dict[str, list[str]] = {}
    # (a) tag evidence
    for t in ntags:
        for topic in TAG_MAP.get(t, []):
            topics.add(topic)
            evidence.setdefault(topic, []).append(f"tag:{t}")
    # papers: tag or title convention
    if ntags & {"paper", "papers", "book"} or re.match(r"^(paper|book)\b[:\s]", title, re.I):
        topics.add(PAPERS)
        evidence.setdefault(PAPERS, []).append("tag/title")
    # (b)+(c) keyword evidence on title and full text
    for topic, pats in KWX.items():
        if not pats:
            continue
        title_hits = [p.pattern for p in pats if p.search(title)]
        if title_hits:
            topics.add(topic)
            evidence.setdefault(topic, []).append(f"title:{title_hits[0]}")
            continue
        distinct = []
        strong = False
        for p in pats:
            n = len(p.findall(text))
            if n:
                distinct.append(p.pattern)
                if n >= STRONG_OCCURRENCES:
                    strong = True
        if len(distinct) >= DISTINCT_MIN or (len(distinct) >= 2 and strong):
            topics.add(topic)
            evidence.setdefault(topic, []).append(f"text:{len(distinct)}kw")
    # company: deeper threshold for text-only hits
    if COMPANY in topics and not any(e.startswith(("tag:", "title:")) for e in evidence.get(COMPANY, [])):
        if not any(len(p.findall(text)) >= COMPANY_COUNT_MIN for p in KWX[COMPANY]):
            topics.discard(COMPANY)
    return [t for t in TOPIC_ORDER if t in topics]


def main() -> None:
    arts = json.loads((BASE / "articles.json").read_text())
    changes = []
    n_add = n_rem = 0
    for art in arts:
        k = __import__("hashlib").sha1(art["url"].encode()).hexdigest()[:16]
        f = BASE / "article_text" / f"{k}.txt"
        tags, text = [], ""
        if f.exists():
            d = json.loads(f.read_text())
            tags, text = d["tags"], d["text"]
        old = art.get("topics", [])
        new = classify(art, tags, text)
        art["topics"] = new
        art["site_tags"] = tags
        added = [t for t in new if t not in old]
        removed = [t for t in old if t not in new]
        if added or removed:
            n_add += len(added)
            n_rem += len(removed)
            changes.append({
                "url": art["url"], "title": art["title"],
                "added": added, "removed": removed, "now": new,
            })
    (BASE / "articles_v2.json").write_text(json.dumps(arts, indent=1))
    (BASE / "classification_changes.json").write_text(json.dumps(changes, indent=1))

    counts = Counter(t for a in arts for t in a["topics"])
    print(f"articles={len(arts)} changed={len(changes)} topic-adds={n_add} topic-removes={n_rem}")
    for t in TOPIC_ORDER:
        print(f"  {t}: {counts.get(t, 0)}")
    print(f"  uncategorized: {sum(1 for a in arts if not a['topics'])}")


if __name__ == "__main__":
    main()
