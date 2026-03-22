#!/usr/bin/env python3
"""Verify fixture outputs against expected JSON, optionally by running a local blux-ca engine command."""
from __future__ import annotations

import argparse
import os
import pathlib
import shlex
import subprocess
import sys
import tempfile
from typing import Any, Iterable

from dataset_common import canonical_dumps, fixture_dirs, load_json, normalize, read_dataset_version



def expected_dir(
    expected_root: pathlib.Path,
    fixture: str,
    model_version: str,
    policy_pack: str,
    *,
    profile_id: str | None = None,
    archive_version: str | None = None,
) -> pathlib.Path:
    if archive_version:
        return expected_root / fixture / "archives" / archive_version / policy_pack
    base = expected_root / fixture / "expected" / model_version
    if profile_id:
        profile_root = base / profile_id
        policy_pack_dir = profile_root / policy_pack
        return policy_pack_dir if policy_pack_dir.exists() else profile_root
    return base / policy_pack



def payload_contains(expected: Any, actual: Any) -> bool:
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return False
        return all(k in actual and payload_contains(v, actual[k]) for k, v in expected.items())
    if isinstance(expected, list):
        if not isinstance(actual, list) or len(expected) != len(actual):
            return False
        return all(payload_contains(e, a) for e, a in zip(expected, actual))
    return expected == actual



def compare_payloads(errors: list[str], label: str, expected_path: pathlib.Path, actual_path: pathlib.Path, fixture: str) -> None:
    expected = normalize(load_json(expected_path))
    actual = normalize(load_json(actual_path))
    if canonical_dumps(expected) == canonical_dumps(actual):
        return
    if payload_contains(expected, actual):
        return
    errors.append(f"{label} mismatch for fixture '{fixture}'")



def compare_fixture(name: str, expected_root: pathlib.Path, actual_root: pathlib.Path, model_version: str, policy_pack: str, profile_id: str | None) -> list[str]:
    errors: list[str] = []
    expected_base = expected_dir(expected_root, name, model_version, policy_pack, profile_id=profile_id)

    if profile_id and not expected_base.exists():
        expected_base = expected_dir(expected_root, name, model_version, policy_pack)
    if not expected_base.exists() and policy_pack != "cA-pro":
        expected_base = expected_dir(expected_root, name, model_version, "cA-pro", profile_id=profile_id)
        if profile_id and not expected_base.exists():
            expected_base = expected_dir(expected_root, name, model_version, "cA-pro")

    expected_paths = {
        "artifact": expected_base / "expected_artifact.json",
        "verdict": expected_base / "expected_verdict.json",
        "report": expected_base / "report.json",
    }
    actual_paths = {
        "artifact": actual_root / name / "artifact.json",
        "verdict": actual_root / name / "verdict.json",
        "report": actual_root / name / "report.json",
    }

    for key in ("artifact", "verdict"):
        if not expected_paths[key].exists():
            errors.append(f"Missing expected file {expected_paths[key]}")
        if not actual_paths[key].exists():
            errors.append(f"Missing actual file {actual_paths[key]}")

    if errors:
        return errors

    compare_payloads(errors, "Artifact", expected_paths["artifact"], actual_paths["artifact"], name)
    compare_payloads(errors, "Verdict", expected_paths["verdict"], actual_paths["verdict"], name)

    if expected_paths["report"].exists():
        if not actual_paths["report"].exists():
            errors.append(f"Missing actual file {actual_paths['report']}")
        else:
            compare_payloads(errors, "Report", expected_paths["report"], actual_paths["report"], name)

    return errors



def compare_archives(fixture: str, expected_root: pathlib.Path, archive_root: pathlib.Path, policy_pack: str, versions: Iterable[str]) -> list[str]:
    errors: list[str] = []
    for version in versions:
        expected_base = expected_dir(expected_root, fixture, model_version=version, policy_pack=policy_pack, archive_version=version)
        if not expected_base.exists() and policy_pack != "cA-pro":
            expected_base = expected_dir(expected_root, fixture, model_version=version, policy_pack="cA-pro", archive_version=version)
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
        local_errors: list[str] = []
        for key in ("artifact", "verdict"):
            if not expected_paths[key].exists():
                local_errors.append(f"Missing expected file {expected_paths[key]}")
            if not actual_paths[key].exists():
                local_errors.append(f"Missing actual file {actual_paths[key]}")
        if local_errors:
            errors.extend(local_errors)
            continue
        compare_payloads(errors, f"Artifact ({version})", expected_paths["artifact"], actual_paths["artifact"], fixture)
        compare_payloads(errors, f"Verdict ({version})", expected_paths["verdict"], actual_paths["verdict"], fixture)
        if expected_paths["report"].exists():
            if not actual_paths["report"].exists():
                errors.append(f"Missing actual file {actual_paths['report']}")
            else:
                compare_payloads(errors, f"Report ({version})", expected_paths["report"], actual_paths["report"], fixture)
    return errors



def render_engine_command(template: str, *, fixture: str, goal: pathlib.Path, out_dir: pathlib.Path, model_version: str, policy_pack: str, profile: str | None) -> list[str]:
    command = template.format(
        fixture=fixture,
        goal=goal.as_posix(),
        out_dir=out_dir.as_posix(),
        model_version=model_version,
        policy_pack=policy_pack,
        profile=profile or "",
    )
    return shlex.split(command)



def run_engine_for_fixtures(command_template: str, expected_root: pathlib.Path, actual_root: pathlib.Path, model_version: str, policy_pack: str, profile_id: str | None) -> None:
    for fixture_dir in fixture_dirs(expected_root):
        out_dir = actual_root / fixture_dir.name
        out_dir.mkdir(parents=True, exist_ok=True)
        cmd = render_engine_command(
            command_template,
            fixture=fixture_dir.name,
            goal=fixture_dir / "goal.json",
            out_dir=out_dir,
            model_version=model_version,
            policy_pack=policy_pack,
            profile=profile_id,
        )
        subprocess.run(cmd, check=True)



def main() -> int:
    parser = argparse.ArgumentParser(description="Compare actual blux-ca outputs to expected fixture artifacts/verdicts.")
    parser.add_argument("--expected-root", default="fixtures", help="Path to fixtures directory containing expected outputs.")
    parser.add_argument("--actual-root", default=None, help="Path containing actual outputs. Each fixture should have artifact.json + verdict.json.")
    parser.add_argument("--model-version", default=None, help="Model version to compare against (defaults to DATASET_VERSION when present).")
    parser.add_argument("--policy-pack", default="cA-pro", help="Policy pack identifier for expected outputs.")
    parser.add_argument("--profile", default=None, help="Optional profile identifier for profile-specific expectations.")
    parser.add_argument("--engine-cmd", default=os.environ.get("BLUX_CA_ENGINE_CMD"), help="Optional command template to run the local blux-ca engine. Available placeholders: {fixture} {goal} {out_dir} {model_version} {policy_pack} {profile}.")
    parser.add_argument("--include-archives", action="store_true", help="Also compare archived outputs stored under fixtures/<case>/archives.")
    parser.add_argument("--archive-versions", default="cA-0.4,cA-0.5,cA-0.6,cA-0.7,cA-0.8,cA-0.9,cA-1.0", help="Comma-separated archived versions to compare when --include-archives is set.")
    parser.add_argument("--archive-actual-root", default=None, help="Root directory containing archived actual outputs (defaults to <actual-root>/archives).")
    args = parser.parse_args()

    expected_root = pathlib.Path(args.expected_root)
    model_version = args.model_version or read_dataset_version() or "cA-1.0-pro"
    policy_pack = args.policy_pack
    profile_id = args.profile
    archive_versions = [v.strip() for v in args.archive_versions.split(",") if v.strip()]

    if not expected_root.exists():
        raise SystemExit(f"Expected fixtures directory not found: {expected_root}")
    if not any(expected_root.iterdir()):
        raise SystemExit("No fixtures found to verify.")

    temp_dir: tempfile.TemporaryDirectory[str] | None = None
    if args.actual_root:
        actual_root = pathlib.Path(args.actual_root)
    elif args.engine_cmd:
        temp_dir = tempfile.TemporaryDirectory(prefix="blux-ca-runs-")
        actual_root = pathlib.Path(temp_dir.name)
    else:
        raise SystemExit(
            "Either --actual-root or --engine-cmd/BLUX_CA_ENGINE_CMD is required. "
            "For live-engine verification, pass --engine-cmd '<local blux-ca command template>'."
        )

    if args.engine_cmd:
        try:
            run_engine_for_fixtures(args.engine_cmd, expected_root, actual_root, model_version, policy_pack, profile_id)
        except subprocess.CalledProcessError as exc:
            raise SystemExit(f"Local blux-ca engine command failed: {exc}") from exc

    archive_actual_root = pathlib.Path(args.archive_actual_root) if args.archive_actual_root else None
    failures: list[str] = []
    for fixture_dir in fixture_dirs(expected_root):
        failures.extend(compare_fixture(fixture_dir.name, expected_root, actual_root, model_version=model_version, policy_pack=policy_pack, profile_id=profile_id))
        if args.include_archives:
            archive_root = archive_actual_root or actual_root / "archives"
            failures.extend(compare_archives(fixture_dir.name, expected_root, archive_root, policy_pack=policy_pack, versions=archive_versions))

    if temp_dir is not None:
        temp_dir.cleanup()

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    source = "local blux-ca engine command" if args.engine_cmd else f"actual root {actual_root}"
    print(f"All fixtures match expected outputs against {source}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
