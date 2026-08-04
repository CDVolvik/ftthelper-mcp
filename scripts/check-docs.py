#!/usr/bin/env python3
"""Guards this repo against the two ways it has actually broken.

1. The endpoint drifting to the bare domain. That domain redirects to www, and
   HTTP clients drop the Authorization header across an origin change, so a
   config copied from here authenticates as nobody and returns 401 with a
   perfectly valid token. It looks like a broken product, not a broken URL.

2. Documenting an endpoint the app no longer serves. /api/mcp/tokens was removed
   when the settings screen replaced it; this repo kept telling people to curl it
   for another day because nothing connected the two.

Run locally with: python scripts/check-docs.py
"""

from __future__ import annotations

import json
import pathlib
import re
import sys
import tomllib
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
CANONICAL = "https://www.fantasytabletophelper.com/api/mcp"
BARE_ENDPOINT = re.compile(r"https://fantasytabletophelper\.com/api/")
RETIRED_ROUTES = ("/api/mcp/tokens",)
SCHEMA_URL = "https://static.modelcontextprotocol.io/schemas/2025-12-11/server.schema.json"

failures: list[str] = []
notes: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)


def check_examples() -> None:
    """Every example must parse, and must point at the canonical endpoint."""
    for path in sorted((ROOT / "examples").iterdir()):
        if path.suffix == ".json":
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                fail(f"{path.name}: not valid JSON -- {exc}")
                continue
            urls = [
                s["url"]
                for s in data.get("mcpServers", {}).values()
                if isinstance(s, dict) and "url" in s
            ]
        elif path.suffix == ".toml":
            try:
                data = tomllib.loads(path.read_text(encoding="utf-8"))
            except tomllib.TOMLDecodeError as exc:
                fail(f"{path.name}: not valid TOML -- {exc}")
                continue
            urls = [
                s["url"]
                for s in data.get("mcp_servers", {}).values()
                if isinstance(s, dict) and "url" in s
            ]
        else:
            continue

        if not urls:
            fail(f"{path.name}: no server url found -- did the config shape change?")
        for url in urls:
            if url != CANONICAL:
                fail(f"{path.name}: url is {url!r}, expected {CANONICAL!r}")

        # A BOM here is not cosmetic: strict JSON parsers reject it, and it has
        # been introduced by accident before by a UTF-8-with-BOM writer.
        if path.read_bytes().startswith(b"\xef\xbb\xbf"):
            fail(f"{path.name}: starts with a UTF-8 BOM")


def check_prose() -> None:
    """The README must not send anyone to the bare domain or a retired route."""
    for path in [ROOT / "README.md", ROOT / "examples" / "README.md"]:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), 1):
            # The warning section quotes the bare URL on purpose, to show what
            # not to do. Anything else mentioning it is a live trap.
            if BARE_ENDPOINT.search(line) and "stripped in transit" not in line:
                fail(f"{path.name}:{lineno}: bare-domain API URL -- {line.strip()[:70]}")
            for route in RETIRED_ROUTES:
                if route in line:
                    fail(f"{path.name}:{lineno}: retired route {route} -- {line.strip()[:70]}")


def check_server_json() -> None:
    """server.json must point at the canonical endpoint and match the schema."""
    path = ROOT / "server.json"
    if not path.exists():
        fail("server.json is missing")
        return

    doc = json.loads(path.read_text(encoding="utf-8"))
    for remote in doc.get("remotes", []):
        if remote.get("url") != CANONICAL:
            fail(f"server.json: remote url is {remote.get('url')!r}, expected {CANONICAL!r}")

    try:
        with urllib.request.urlopen(SCHEMA_URL, timeout=20) as resp:
            schema = json.load(resp)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        # A registry CDN blip must not turn this repo red. The URL checks above
        # already ran; only the schema half is skipped.
        notes.append(f"schema fetch failed, skipped schema validation ({exc})")
        return

    try:
        from jsonschema import Draft7Validator
    except ImportError:
        notes.append("jsonschema not installed, skipped schema validation")
        return

    errors = sorted(Draft7Validator(schema).iter_errors(doc), key=lambda e: list(e.path))
    for err in errors:
        loc = "/".join(str(p) for p in err.path) or "(root)"
        fail(f"server.json: {loc}: {err.message}")


def main() -> int:
    check_examples()
    check_prose()
    check_server_json()

    for note in notes:
        print(f"note: {note}")
    if failures:
        print(f"\n{len(failures)} problem(s):")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("ok: examples, README and server.json all agree on the canonical endpoint")
    return 0


if __name__ == "__main__":
    sys.exit(main())
