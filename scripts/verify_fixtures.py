#!/usr/bin/env python3
"""Verify cA fixture outputs against expected JSON bytes."""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any


def canonical_bytes(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def load_json(path: pathlib.Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc


def compare_fixture(name: str, expected_root: pathlib.Path, actual_root: pathlib.Path) -> list[str]:
    errors: list[str] = []
    expected_artifact = expected_root / name / "expected_artifact.json"
    expected_verdict = expected_root / name / "expected_verdict.json"
    actual_artifact = actual_root / name / "artifact.json"
    actual_verdict = actual_root / name / "verdict.json"

    for path in (expected_artifact, expected_verdict, actual_artifact, actual_verdict):
        if not path.exists():
            errors.append(f"Missing {path}")

    if errors:
        return errors

    if canonical_bytes(load_json(expected_artifact)) != canonical_bytes(load_json(actual_artifact)):
        errors.append(f"Artifact mismatch for fixture '{name}'")

    if canonical_bytes(load_json(expected_verdict)) != canonical_bytes(load_json(actual_verdict)):
        errors.append(f"Verdict mismatch for fixture '{name}'")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare actual cA outputs to expected fixture artifacts/verdicts."
    )
    parser.add_argument(
        "--expected-root",
        default="fixtures",
        help="Path to fixtures directory containing expected outputs.",
    )
    parser.add_argument(
        "--actual-root",
        required=True,
        help="Path containing actual outputs. Each fixture should have artifact.json + verdict.json.",
    )
    args = parser.parse_args()

    expected_root = pathlib.Path(args.expected_root)
    actual_root = pathlib.Path(args.actual_root)

    if not expected_root.exists():
        raise SystemExit(f"Expected fixtures directory not found: {expected_root}")

    fixture_dirs = sorted(p.name for p in expected_root.iterdir() if p.is_dir())
    if not fixture_dirs:
        raise SystemExit("No fixtures found to verify.")

    failures: list[str] = []
    for name in fixture_dirs:
        failures.extend(compare_fixture(name, expected_root, actual_root))

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print("All fixtures match expected outputs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
