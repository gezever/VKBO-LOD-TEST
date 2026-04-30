#!/usr/bin/env python3
"""Check all vestigingen URIs from vestigingen.csv for dereference and content negotiation."""
import csv
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from vkbo_lod.deref import check_vestiging


def load_uris(csv_path: Path) -> list[str]:
    uris = []
    with open(csv_path) as f:
        for line in f:
            line = line.strip()
            if line:
                uris.append(line)
    return uris


def main() -> None:
    csv_path = Path(__file__).parent.parent / "sources" / "vestigingen.csv"
    uris = load_uris(csv_path)
    print(f"Checking {len(uris)} vestigingen...", file=sys.stderr)

    writer = csv.writer(sys.stdout)
    writer.writerow([
        "vestiging_uri", "v_status", "v_content_type", "v_valid_turtle",
        "linked_onderneming", "o_status", "o_valid_turtle", "error",
    ])

    with httpx.Client(timeout=30) as client:
        for i, uri in enumerate(uris, 1):
            v, o = check_vestiging(uri, client)
            writer.writerow([
                v.uri,
                v.status_code or "",
                v.content_type or "",
                v.is_valid_turtle,
                v.linked_onderneming or "",
                o.status_code if o else "",
                o.is_valid_turtle if o else "",
                v.error or (o.error if o else "") or "",
            ])
            if i % 10 == 0:
                print(f"  {i}/{len(uris)}", file=sys.stderr)


if __name__ == "__main__":
    main()
