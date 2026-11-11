#!/usr/bin/env python3
"""Run WhatFontIs API 2.2 (pro mode) on clean type specimens from the comp (via curl for CF bypass)."""
import base64
import json
import subprocess

API_KEY = "wfi_mcp_f1d77c5a65c179afe9006394c7e9f32e"
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

SPECIMENS = [
    ("sections-label", "/tmp/typeid/wfi-sections.png"),
    ("rail-row1-line1", "/tmp/typeid/wfi-row1line1.png"),
    ("rail-row2", "/tmp/typeid/wfi-row2.png"),
    ("section-title", "/tmp/typeid/wfi-sectiontitle.png"),
    ("masthead", "/tmp/typeid/wfi-masthead.png"),
]

def identify(name: str, path: str) -> None:
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    cmd = [
        "curl", "-s", "-m", "180",
        "-A", UA,
        "-X", "POST", "https://www.whatfontis.com/api2/",
        "--data-urlencode", f"API_KEY={API_KEY}",
        "--data-urlencode", "IMAGEBASE64=1",
        "--data-urlencode", f"urlimagebase64={b64}",
        "--data-urlencode", "NOTTEXTBOXSDETECTION=0",
        "--data-urlencode", "limit=8",
        "--data-urlencode", "mode=pro",
    ]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout.strip()
    print(f"=== {name} ===")
    if out.startswith("["):
        for m in json.loads(out):
            print(f"  {m.get('title'):36s} {m.get('type'):12s} {m.get('site','')}")
    else:
        print("  RAW:", out[:300])

for n, p in SPECIMENS:
    identify(n, p)
