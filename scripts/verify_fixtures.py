#!/usr/bin/env python3
"""Verify dataset fixtures against stored expectations or a live local blux-ca checkout."""
from __future__ import annotations

import argparse
import json
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
    }
    actual_paths = {
        "artifact": actual_root / name / "artifact.json",
        "verdict": actual_root / name / "verdict.json",
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
        }
        actual_paths = {
            "artifact": actual_base / "artifact.json",
            "verdict": actual_base / "verdict.json",
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
    return [part for part in shlex.split(command) if part]


def _bridge_request_for_fixture(name: str, policy_pack: str) -> dict[str, Any]:
    if name == "multi_file_artifact":
        return {
            "language": "python",
            "files": [
                {"path": "README.md", "content": "# multi-file\n"},
                {"path": "main.py", "content": "print('multi file')\n"},
            ],
        }
    if name == "patch_bundle":
        return {
            "artifact_type": "patch_bundle",
            "language": "python",
            "patches": [
                {"path": "main.py", "unified_diff": "--- /dev/null\n+++ main.py\n@@ -0,0 +1 @@\n+print('patch bundle')\n"},
            ],
        }
    if name == "minimal_delta":
        return {"language": "python", "files": [{"path": "main.py", "content": "print('delta')\n"}]}
    if name == "validator_pack":
        return {"language": "python", "files": [{"path": "validator.py", "content": "print('validator pack')\n"}]}
    if name == "policy_pack_matrix":
        content = "print('policy pack matrix')\n"
        if policy_pack == "cA-mini":
            content = "# TODO: blocked in mini\nprint('policy pack matrix')\n"
        return {"language": "python", "policy_pack_id": policy_pack, "policy_pack_version": "1.0", "files": [{"path": "main.py", "content": content}]}
    if name == "profile_echo":
        return {"language": "python", "files": [{"path": "main.py", "content": "print('profile echo')\n"}]}
    if name == "legacy_outputs":
        return {"language": "python", "files": [{"path": "legacy.py", "content": "print('legacy')\n"}]}
    if name == "drift_probe":
        return {"language": "python", "files": [{"path": "main.py", "content": "print('future enhancement')\n"}]}
    if name == "conflict_detection":
        return {"artifact_type": "patch_bundle", "language": "python", "patches": [{"path": "main.py", "unified_diff": "--- a/main.py\n+++ b/main.py\n@@ -1 +1 @@\n-print('old')\n+print('new')\n"}, {"path": "main.py", "unified_diff": "--- a/main.py\n+++ b/main.py\n@@ -1 +1 @@\n-print('old')\n+print('other')\n"}]}
    if name == "duplicate_paths":
        return {"language": "python", "files": [{"path": "dup.py", "content": "print('a')\n"}, {"path": "dup.py", "content": "print('b')\n"}]}
    if name == "path_traversal":
        return {"language": "python", "files": [{"path": "../escape.py", "content": "print('escape')\n"}]}
    if name == "unsorted_output":
        return {"language": "python", "files": [{"path": "main.py", "content": "def broken(:\n    pass\n"}]}
    return {"language": "python", "files": [{"path": "main.py", "content": f"print({name!r})\n"}]}


def bridge_goal_for_engine(goal: dict[str, Any], fixture_name: str, policy_pack: str) -> dict[str, Any]:
    metadata = goal.get("metadata") or {}
    constraints: list[str] = []
    goal_id = metadata.get("fixture_id") or fixture_name
    intent = goal.get("prompt") or goal.get("summary") or fixture_name
    if fixture_name == "infeasible":
        constraints = ["ALLOW_PATCH", "DENY_PATCH"]
    elif fixture_name == "missing_inputs":
        intent = ""
    request = _bridge_request_for_fixture(fixture_name, policy_pack)
    return {
        "contract_version": "0.2",
        "goal_id": goal_id,
        "intent": intent,
        "constraints": constraints,
        "request": request,
    }


def _write_engine_bridge_fixtures(expected_root: pathlib.Path, dest_root: pathlib.Path, policy_pack: str) -> None:
    for fixture_dir in fixture_dirs(expected_root):
        goal = load_json(fixture_dir / "goal.json")
        bridge_dir = dest_root / fixture_dir.name
        bridge_dir.mkdir(parents=True, exist_ok=True)
        (bridge_dir / "goal.json").write_text(
            json.dumps(bridge_goal_for_engine(goal, fixture_dir.name, policy_pack), indent=2) + "\n",
            encoding="utf-8",
        )


def _effective_profile(profile_id: str | None) -> str | None:
    value = (profile_id or "").strip()
    if not value or value == "default":
        return None
    return value


def run_engine_acceptance(engine_root: pathlib.Path, expected_root: pathlib.Path, actual_root: pathlib.Path, policy_pack: str, profile_id: str | None, python_bin: str) -> None:
    with tempfile.TemporaryDirectory(prefix="blux-ca-bridge-fixtures-") as bridge_tmp:
        bridge_root = pathlib.Path(bridge_tmp)
        _write_engine_bridge_fixtures(expected_root, bridge_root, policy_pack)
        cmd = [python_bin, "-m", "blux_ca", "accept", "--fixtures", bridge_root.as_posix(), "--out", actual_root.as_posix()]
        effective_profile = _effective_profile(profile_id)
        if effective_profile:
            cmd.extend(["--profile", effective_profile])
        env = os.environ.copy()
        src_path = (engine_root / "src").as_posix()
        env["PYTHONPATH"] = src_path if not env.get("PYTHONPATH") else f"{src_path}:{env['PYTHONPATH']}"
        subprocess.run(cmd, check=True, cwd=engine_root, env=env)


def compare_engine_verification(name: str, expected_root: pathlib.Path, actual_root: pathlib.Path, model_version: str, policy_pack: str, profile_id: str | None) -> list[str]:
    errors: list[str] = []
    expected_base = expected_dir(expected_root, name, model_version, policy_pack, profile_id=profile_id)
    if profile_id and not expected_base.exists():
        expected_base = expected_dir(expected_root, name, model_version, policy_pack)
    expected_verdict_path = expected_base / "expected_verdict.json"
    expected_artifact_path = expected_base / "expected_artifact.json"
    if (not expected_verdict_path.exists() or not expected_artifact_path.exists()) and policy_pack != "cA-pro":
        fallback_base = expected_dir(expected_root, name, model_version, "cA-pro", profile_id=profile_id)
        if profile_id and not fallback_base.exists():
            fallback_base = expected_dir(expected_root, name, model_version, "cA-pro")
        expected_base = fallback_base
        expected_verdict_path = expected_base / "expected_verdict.json"
        expected_artifact_path = expected_base / "expected_artifact.json"
    if not expected_verdict_path.exists() or not expected_artifact_path.exists():
        return [f"Missing expected engine-bridge bundle for fixture '{name}'"]

    report_path = actual_root / "report.json"
    if not report_path.exists():
        return [f"Missing actual acceptance report {report_path}"]
    report = load_json(report_path)
    rows = {row.get("fixture"): row for row in report.get("fixtures", []) if isinstance(row, dict)}
    row = rows.get(name)
    if row is None:
        return [f"Missing acceptance report row for fixture '{name}'"]

    expected_verdict = load_json(expected_verdict_path)
    expected_artifact = load_json(expected_artifact_path)
    actual_artifact_path = actual_root / name / "artifact.json"
    actual_verdict_path = actual_root / name / "verdict.json"
    if not actual_artifact_path.exists() or not actual_verdict_path.exists():
        return [f"Missing actual artifact/verdict files for fixture '{name}'"]
    actual_artifact = load_json(actual_artifact_path)
    actual_verdict = load_json(actual_verdict_path)

    expected_outcome = str(expected_verdict.get("outcome", "")).lower()
    actual_outcome = str(row.get("status", "")).lower()
    if actual_outcome != expected_outcome:
        errors.append(f"Outcome mismatch for fixture '{name}': expected {expected_outcome}, got {actual_outcome}")

    expected_request = expected_verdict.get("request") or {}
    expected_pack = expected_request.get("policy_pack_id")
    if row.get("policy_pack_id") != expected_pack:
        errors.append(f"Policy pack mismatch for fixture '{name}': expected {expected_pack}, got {row.get('policy_pack_id')}")
    if actual_artifact.get("policy_pack_id") != expected_pack or actual_verdict.get("policy_pack_id") != expected_pack:
        errors.append(f"Raw engine policy pack mismatch for fixture '{name}'")

    expected_profile = _effective_profile(profile_id)
    if expected_profile:
        if report.get("profile_id") != expected_profile:
            errors.append(f"Acceptance report profile mismatch: expected {expected_profile}, got {report.get('profile_id')}")
        if actual_artifact.get("run", {}).get("profile_id") != expected_profile:
            errors.append(f"Artifact run.profile_id mismatch for fixture '{name}'")
        if actual_verdict.get("run", {}).get("profile_id") != expected_profile:
            errors.append(f"Verdict run.profile_id mismatch for fixture '{name}'")
    else:
        if "profile_id" in report:
            errors.append("Acceptance report unexpectedly emitted profile metadata without --profile")

    if actual_artifact.get("model_version") != "cA-1.0-pro":
        errors.append(f"Artifact model_version mismatch for fixture '{name}'")
    if actual_verdict.get("model_version") != "cA-1.0-pro":
        errors.append(f"Verdict model_version mismatch for fixture '{name}'")
    if expected_artifact.get("request", {}).get("policy_pack_version") != row.get("policy_pack_version"):
        errors.append(f"Policy pack version mismatch for fixture '{name}'")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare actual blux-ca outputs to expected fixture artifacts/verdicts.")
    parser.add_argument("--expected-root", default="fixtures", help="Path to fixtures directory containing expected outputs.")
    parser.add_argument("--actual-root", default=None, help="Path containing actual outputs. Each fixture should have artifact.json + verdict.json.")
    parser.add_argument("--model-version", default=None, help="Model version to compare against (defaults to DATASET_VERSION when present).")
    parser.add_argument("--policy-pack", default="cA-pro", help="Dataset policy pack bundle to compare against.")
    parser.add_argument("--profile", default=None, help="Optional dataset profile bundle to compare against. Use the real engine profile id (for example cpu) only when needed; omit for the default engine run.")
    parser.add_argument("--engine-root", default=os.environ.get("BLUX_CA_ENGINE_ROOT"), help="Path to a real local blux-ca checkout. Uses the supported CLI: python -m blux_ca accept --fixtures <generated-bridge-dir> --out <actual-root> [--profile <id>].")
    parser.add_argument("--engine-python", default=sys.executable, help="Python interpreter to use with --engine-root (default: current interpreter).")
    parser.add_argument("--engine-cmd", default=os.environ.get("BLUX_CA_ENGINE_CMD"), help="Optional custom command template for dataset-format outputs. Available placeholders: {fixture} {goal} {out_dir} {model_version} {policy_pack} {profile}.")
    parser.add_argument("--include-archives", action="store_true", help="Also compare archived outputs stored under fixtures/<case>/archives. Only supported with --actual-root or --engine-cmd dataset-format outputs.")
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
    if args.engine_root and args.engine_cmd:
        raise SystemExit("Use either --engine-root or --engine-cmd, not both.")
    if args.include_archives and args.engine_root:
        raise SystemExit("--include-archives is not supported with --engine-root because archived bundles target historical engine lines.")

    temp_dir: tempfile.TemporaryDirectory[str] | None = None
    if args.actual_root:
        actual_root = pathlib.Path(args.actual_root)
    elif args.engine_root or args.engine_cmd:
        temp_dir = tempfile.TemporaryDirectory(prefix="blux-ca-runs-")
        actual_root = pathlib.Path(temp_dir.name)
    else:
        raise SystemExit(
            "Either --actual-root, --engine-root/BLUX_CA_ENGINE_ROOT, or --engine-cmd/BLUX_CA_ENGINE_CMD is required."
        )

    verification_mode = "dataset-format"
    if args.engine_root:
        verification_mode = "engine-root"
        try:
            run_engine_acceptance(pathlib.Path(args.engine_root), expected_root, actual_root, policy_pack, profile_id, args.engine_python)
        except subprocess.CalledProcessError as exc:
            raise SystemExit(f"Local blux-ca acceptance command failed: {exc}") from exc
    elif args.engine_cmd:
        for fixture_dir in fixture_dirs(expected_root):
            out_dir = actual_root / fixture_dir.name
            out_dir.mkdir(parents=True, exist_ok=True)
            cmd = render_engine_command(
                args.engine_cmd,
                fixture=fixture_dir.name,
                goal=fixture_dir / "goal.json",
                out_dir=out_dir,
                model_version=model_version,
                policy_pack=policy_pack,
                profile=_effective_profile(profile_id),
            )
            try:
                subprocess.run(cmd, check=True)
            except subprocess.CalledProcessError as exc:
                raise SystemExit(f"Local blux-ca engine command failed: {exc}") from exc

    archive_actual_root = pathlib.Path(args.archive_actual_root) if args.archive_actual_root else None
    failures: list[str] = []
    for fixture_dir in fixture_dirs(expected_root):
        if verification_mode == "engine-root":
            failures.extend(compare_engine_verification(fixture_dir.name, expected_root, actual_root, model_version=model_version, policy_pack=policy_pack, profile_id=profile_id))
        else:
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

    if verification_mode == "engine-root":
        source = f"local blux-ca checkout {args.engine_root}"
    else:
        source = "local blux-ca engine command" if args.engine_cmd else f"actual root {actual_root}"
    print(f"All fixtures match expected outputs against {source}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
