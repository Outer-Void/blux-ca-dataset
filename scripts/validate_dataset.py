#!/usr/bin/env python3
"""Validate fixture layout and dataset versions."""
from __future__ import annotations

import json
import pathlib
import sys

DATASET_VERSION_PATH = pathlib.Path("DATASET_VERSION")


def load_json(path: pathlib.Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc


def get_dataset_version() -> str:
    if not DATASET_VERSION_PATH.exists():
        raise SystemExit("DATASET_VERSION file missing.")
    return DATASET_VERSION_PATH.read_text(encoding="utf-8").strip()


def expect_version(path: pathlib.Path, expected: str, errors: list[str]) -> None:
    data = load_json(path)
    version = data.get("version")
    if version != expected:
        errors.append(f"Version mismatch in {path}: expected {expected}, got {version}")


def validate_fixture(fixture_dir: pathlib.Path, dataset_version: str) -> list[str]:
    errors: list[str] = []
    goal = fixture_dir / "goal.json"
    if not goal.exists():
        errors.append(f"Missing {goal}")
        return errors

    expect_version(goal, dataset_version, errors)

    expected_root = fixture_dir / "expected" / dataset_version
    if not expected_root.exists():
        errors.append(f"Missing expected outputs for {fixture_dir.name}: {expected_root}")
        return errors

    policy_packs = [p for p in expected_root.iterdir() if p.is_dir()]
    if not policy_packs:
        errors.append(f"No policy pack directories found in {expected_root}")
        return errors

    for pack_dir in policy_packs:
        for name in ("expected_artifact.json", "expected_verdict.json"):
            path = pack_dir / name
            if not path.exists():
                errors.append(f"Missing {path}")
                continue
            expect_version(path, dataset_version, errors)

        report = pack_dir / "report.json"
        if report.exists():
            expect_version(report, dataset_version, errors)

    archive_root = fixture_dir / "archives"
    if archive_root.exists():
        for version_dir in archive_root.iterdir():
            if not version_dir.is_dir():
                continue
            for pack_dir in version_dir.iterdir():
                if not pack_dir.is_dir():
                    continue
                for name in ("expected_artifact.json", "expected_verdict.json"):
                    path = pack_dir / name
                    if not path.exists():
                        errors.append(f"Missing {path}")
                        continue
                    expect_version(path, version_dir.name, errors)
                report = pack_dir / "report.json"
                if report.exists():
                    expect_version(report, version_dir.name, errors)

    return errors


def main() -> int:
    dataset_version = get_dataset_version()
    fixture_root = pathlib.Path("fixtures")
    if not fixture_root.exists():
        raise SystemExit("fixtures directory missing.")

    failures: list[str] = []
    for fixture_dir in sorted(p for p in fixture_root.iterdir() if p.is_dir()):
        failures.extend(validate_fixture(fixture_dir, dataset_version))

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print("Fixture layout and versions validated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
