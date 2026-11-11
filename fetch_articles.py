#!/usr/bin/env python3
"""Fetch every article page (resumable). Statuses recorded in fetch_status.json."""
import concurrent.futures as cf
import hashlib
import json
import pathlib
import random
import time
import urllib.request

BASE = pathlib.Path(__file__).resolve().parent
DEST = BASE / "articles_html"
DEST.mkdir(exist_ok=True)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
arts = json.loads((BASE / "articles.json").read_text())
STATUS_FILE = BASE / "fetch_status.json"
status = json.loads(STATUS_FILE.read_text()) if STATUS_FILE.exists() else {}


def key_for(url: str) -> str:
    return hashlib.sha1(url.encode()).hexdigest()[:16]


def fetch(art: dict) -> tuple[str, str]:
    url = art["url"]
    k = key_for(url)
    if status.get(k, {}).get("state") == "ok":
        return k, "cached"
    dest = DEST / f"{k}.html"
    if dest.exists() and dest.stat().st_size > 5000:
        status[k] = {"url": url, "state": "ok", "final_url": url, "size": dest.stat().st_size}
        return k, "cached-file"
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
                final = r.geturl()
            dest.write_bytes(data)
            status[k] = {"url": url, "state": "ok", "final_url": final, "size": len(data)}
            return k, f"ok {len(data)}"
        except urllib.error.HTTPError as e:
            if e.code in (404, 410):
                status[k] = {"url": url, "state": "dead", "code": e.code}
                return k, f"DEAD {e.code}"
            if attempt == 3:
                status[k] = {"url": url, "state": "error", "code": e.code}
                return k, f"FAIL {e.code}"
        except Exception as e:
            if attempt == 3:
                status[k] = {"url": url, "state": "error", "err": str(e)[:120]}
                return k, f"FAIL {e}"
        time.sleep(1.5 * (attempt + 1) + random.random())
    return k, "FAIL"


def main() -> None:
    todo = [a for a in arts if status.get(key_for(a["url"]), {}).get("state") != "ok"]
    print(f"to fetch: {len(todo)} (of {len(arts)})")
    done = 0
    with cf.ThreadPoolExecutor(max_workers=6) as ex:
        for k, s in ex.map(fetch, todo):
            done += 1
            if done % 50 == 0 or "FAIL" in s or "DEAD" in s:
                print(f"[{done}/{len(todo)}] {s} {status[k]['url']}", flush=True)
            if done % 200 == 0:
                STATUS_FILE.write_text(json.dumps(status))
    STATUS_FILE.write_text(json.dumps(status))
    ok = sum(1 for v in status.values() if v["state"] == "ok")
    dead = sum(1 for v in status.values() if v["state"] == "dead")
    err = sum(1 for v in status.values() if v["state"] == "error")
    print(f"\nstatus: ok={ok} dead={dead} error={err} total={len(arts)}")


if __name__ == "__main__":
    main()
