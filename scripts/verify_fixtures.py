#!/usr/bin/env python3
"""Verify cA fixture outputs against expected JSON bytes."""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any, Iterable

DATASET_VERSION_PATH = pathlib.Path("DATASET_VERSION")


def canonical_bytes(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )


def load_json(path: pathlib.Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc


def read_dataset_version() -> str | None:
    if DATASET_VERSION_PATH.exists():
        return DATASET_VERSION_PATH.read_text(encoding="utf-8").strip()
    return None


def expected_dir(
    expected_root: pathlib.Path,
    fixture: str,
    model_version: str,
    policy_pack: str,
    *,
    archive_version: str | None = None,
) -> pathlib.Path:
    if archive_version:
        return expected_root / fixture / "archives" / archive_version / policy_pack
    return expected_root / fixture / "expected" / model_version / policy_pack


def legacy_expected_paths(expected_root: pathlib.Path, fixture: str) -> dict[str, pathlib.Path]:
    return {
        "artifact": expected_root / fixture / "expected_artifact.json",
        "verdict": expected_root / fixture / "expected_verdict.json",
        "report": expected_root / fixture / "report.json",
    }


def compare_payloads(
    errors: list[str],
    label: str,
    expected_path: pathlib.Path,
    actual_path: pathlib.Path,
    fixture: str,
) -> None:
    if canonical_bytes(load_json(expected_path)) != canonical_bytes(load_json(actual_path)):
        errors.append(f"{label} mismatch for fixture '{fixture}'")


def compare_fixture(
    name: str,
    expected_root: pathlib.Path,
    actual_root: pathlib.Path,
    model_version: str,
    policy_pack: str,
) -> list[str]:
    errors: list[str] = []
    expected_base = expected_dir(expected_root, name, model_version, policy_pack)

    if expected_base.exists():
        expected_paths = {
            "artifact": expected_base / "expected_artifact.json",
            "verdict": expected_base / "expected_verdict.json",
            "report": expected_base / "report.json",
        }
    else:
        expected_paths = legacy_expected_paths(expected_root, name)

    actual_paths = {
        "artifact": actual_root / name / "artifact.json",
        "verdict": actual_root / name / "verdict.json",
        "report": actual_root / name / "report.json",
    }

    for key in ("artifact", "verdict"):
        if not expected_paths[key].exists():
            errors.append(f"Missing {expected_paths[key]}")
        if not actual_paths[key].exists():
            errors.append(f"Missing {actual_paths[key]}")

    if errors:
        return errors

    compare_payloads(errors, "Artifact", expected_paths["artifact"], actual_paths["artifact"], name)
    compare_payloads(errors, "Verdict", expected_paths["verdict"], actual_paths["verdict"], name)

    if expected_paths["report"].exists():
        if not actual_paths["report"].exists():
            errors.append(f"Missing {actual_paths['report']}")
        else:
            compare_payloads(errors, "Report", expected_paths["report"], actual_paths["report"], name)

    return errors


def compare_archives(
    fixture: str,
    expected_root: pathlib.Path,
    archive_root: pathlib.Path,
    policy_pack: str,
    versions: Iterable[str],
) -> list[str]:
    errors: list[str] = []
    for version in versions:
        expected_base = expected_dir(
            expected_root, fixture, model_version=version, policy_pack=policy_pack, archive_version=version
        )
        if not expected_base.exists():
            continue
        actual_base = archive_root / version / policy_pack / fixture
        expected_paths = {
            "artifact": expected_base / "expected_artifact.json",
            "verdict": expected_base / "expected_verdict.json",
            "report": expected_base / "report.json",
        }
        actual_paths = {
            "artifact": actual_base / "artifact.json",
            "verdict": actual_base / "verdict.json",
            "report": actual_base / "report.json",
        }
        for key in ("artifact", "verdict"):
            if not expected_paths[key].exists():
                errors.append(f"Missing {expected_paths[key]}")
            if not actual_paths[key].exists():
                errors.append(f"Missing {actual_paths[key]}")
        if errors:
            continue
        compare_payloads(
            errors,
            f"Artifact ({version})",
            expected_paths["artifact"],
            actual_paths["artifact"],
            fixture,
        )
        compare_payloads(
            errors,
            f"Verdict ({version})",
            expected_paths["verdict"],
            actual_paths["verdict"],
            fixture,
        )
        if expected_paths["report"].exists():
            if not actual_paths["report"].exists():
                errors.append(f"Missing {actual_paths['report']}")
            else:
                compare_payloads(
                    errors,
                    f"Report ({version})",
                    expected_paths["report"],
                    actual_paths["report"],
                    fixture,
                )
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
    parser.add_argument(
        "--model-version",
        default=None,
        help="Model version to compare against (defaults to DATASET_VERSION when present).",
    )
    parser.add_argument(
        "--policy-pack",
        default="default",
        help="Policy pack identifier for expected outputs.",
    )
    parser.add_argument(
        "--include-archives",
        action="store_true",
        help="Also compare archived outputs stored under fixtures/<case>/archives.",
    )
    parser.add_argument(
        "--archive-versions",
        default="cA-0.4,cA-0.5,cA-0.6,cA-0.7,cA-0.8,cA-0.9,cA-1.0-pro",
        help="Comma-separated archived versions to compare when --include-archives is set.",
    )
    parser.add_argument(
        "--archive-actual-root",
        default=None,
        help="Root directory containing archived actual outputs (defaults to <actual-root>/archives).",
    )
    args = parser.parse_args()

    expected_root = pathlib.Path(args.expected_root)
    actual_root = pathlib.Path(args.actual_root)
    model_version = args.model_version or read_dataset_version() or "cA-1.0"
    policy_pack = args.policy_pack
    archive_versions = [v.strip() for v in args.archive_versions.split(",") if v.strip()]
    archive_actual_root = pathlib.Path(args.archive_actual_root) if args.archive_actual_root else None

    if not expected_root.exists():
        raise SystemExit(f"Expected fixtures directory not found: {expected_root}")

    fixture_dirs = sorted(p.name for p in expected_root.iterdir() if p.is_dir())
    if not fixture_dirs:
        raise SystemExit("No fixtures found to verify.")

    failures: list[str] = []
    for name in fixture_dirs:
        failures.extend(
            compare_fixture(name, expected_root, actual_root, model_version=model_version, policy_pack=policy_pack)
        )
        if args.include_archives:
            archive_root = archive_actual_root or actual_root / "archives"
            failures.extend(
                compare_archives(
                    name,
                    expected_root,
                    archive_root,
                    policy_pack=policy_pack,
                    versions=archive_versions,
                )
            )

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print("All fixtures match expected outputs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
