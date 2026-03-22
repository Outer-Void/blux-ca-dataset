#!/usr/bin/env python3
"""Deterministically export BLUX cA fixtures to JSONL."""
from __future__ import annotations

import argparse
import hashlib
import pathlib
import sys

from dataset_common import build_export_row, canonical_dumps, fixture_dirs, iter_expected_bundles, read_mapping


def sort_key(row: dict) -> tuple[str, int, str, str, str]:
    metadata = row["metadata"]
    return (
        metadata["fixture_id"],
        0 if metadata["archive_version"] is None else 1,
        metadata["archive_version"] or "",
        metadata["profile_id"] or "",
        metadata["policy_pack_id"],
    )



def main() -> int:
    parser = argparse.ArgumentParser(description="Export deterministic BLUX cA JSONL rows.")
    parser.add_argument("--output", default=None, help="Output JSONL path. Defaults to exports/blux-ca-<dataset_version>.jsonl")
    parser.add_argument("--include-archives", action="store_true", help="Include archived compatibility examples in the export.")
    parser.add_argument("--write-sha256", action="store_true", help="Write a sibling .sha256 file for the JSONL output.")
    args = parser.parse_args()

    mapping = read_mapping()
    output = pathlib.Path(args.output or f"exports/blux-ca-{mapping['dataset_version']}.jsonl")
    output.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    for fixture_dir in fixture_dirs():
        for bundle in iter_expected_bundles(fixture_dir, mapping["dataset_version"]):
            if bundle.archive_version is not None and not args.include_archives:
                continue
            rows.append(build_export_row(bundle, mapping))

    rows.sort(key=sort_key)
    jsonl = "".join(f"{canonical_dumps(row)}\n" for row in rows)
    output.write_text(jsonl, encoding="utf-8")
    digest = hashlib.sha256(jsonl.encode("utf-8")).hexdigest()

    if args.write_sha256:
        output.with_suffix(output.suffix + ".sha256").write_text(f"{digest}  {output.name}\n", encoding="utf-8")

    print(f"Exported {len(rows)} rows to {output}.")
    print(f"sha256={digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
