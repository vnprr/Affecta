#!/usr/bin/env python3
"""Convert authored clinical-content Markdown into Affecta ingestion documents.

Each `.md` file with YAML-style front matter is mapped to the shape the
`clinical-rag-agent` ingestion API expects:

    {"source": <id>, "title": <title>, "text": <body>,
     "metadata": {<all other front-matter fields as strings>}}

Usage:
    # dry run: emit the documents JSON the API would receive
    python build_chunks.py ../methods --out documents.json

    # load into a running service
    python build_chunks.py ../methods --api http://localhost:8000 --token local-dev-key

Notes:
- No third-party dependencies. The front-matter parser supports `key: value`,
  inline lists `key: [a, b, c]`, and multi-line `-` bullet lists.
- README.md files are skipped.
"""

import argparse
import json
import sys
import urllib.request
from pathlib import Path


def parse_front_matter(text: str) -> tuple[dict, str]:
    """Return (front_matter_dict, body). Raises ValueError if no front matter."""
    if not text.startswith("---"):
        raise ValueError("missing front matter")
    end = text.find("\n---", 3)
    if end == -1:
        raise ValueError("unterminated front matter")
    raw = text[3:end].strip("\n")
    body = text[end + 4 :].lstrip("\n")
    data: dict = {}
    current_key: str | None = None
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")) and line.lstrip().startswith("- "):
            # continuation of a multi-line list
            if current_key is not None:
                data.setdefault(current_key, [])
                if isinstance(data[current_key], list):
                    data[current_key].append(_clean(line.lstrip()[2:]))
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        current_key = key
        if value == "":
            data[key] = []  # expect bullets to follow
        elif value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            data[key] = [_clean(v) for v in inner.split(",") if v.strip()] if inner else []
        else:
            data[key] = _clean(value)
    return data, body


def _clean(value: str) -> str:
    return value.strip().strip('"').strip("'")


def to_document(fm: dict, body: str, path: Path) -> dict:
    source = fm.get("id")
    if not source:
        raise ValueError(f"{path}: missing 'id'")
    title = fm.get("title", source)
    metadata: dict[str, str] = {}
    for key, value in fm.items():
        if key in {"id", "title"}:
            continue
        metadata[key] = ", ".join(value) if isinstance(value, list) else str(value)
    return {"source": source, "title": title, "text": body.strip(), "metadata": metadata}


def collect(root: Path) -> list[dict]:
    docs = []
    for path in sorted(root.rglob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        text = path.read_text(encoding="utf-8")
        try:
            fm, body = parse_front_matter(text)
        except ValueError as error:
            print(f"skip {path}: {error}", file=sys.stderr)
            continue
        if any(str(v).startswith("REPLACE") for v in fm.values()):
            print(f"skip {path}: contains unfilled REPLACE placeholders", file=sys.stderr)
            continue
        docs.append(to_document(fm, body, path))
    return docs


def post(api: str, token: str, docs: list[dict]) -> None:
    payload = json.dumps({"documents": docs}).encode("utf-8")
    request = urllib.request.Request(
        api.rstrip("/") + "/api/ingest",
        data=payload,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request) as response:
        print(response.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="directory of authored .md content")
    parser.add_argument("--out", type=Path, help="write documents JSON here (dry run)")
    parser.add_argument("--api", help="base URL of a running clinical-rag-agent")
    parser.add_argument("--token", default="local-dev-key", help="API bearer token")
    args = parser.parse_args()

    docs = collect(args.root)
    print(f"collected {len(docs)} document(s)", file=sys.stderr)

    if args.out:
        args.out.write_text(json.dumps(docs, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"wrote {args.out}", file=sys.stderr)
    if args.api:
        post(args.api, args.token, docs)
    if not args.out and not args.api:
        json.dump(docs, sys.stdout, ensure_ascii=False, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
