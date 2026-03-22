#!/usr/bin/env python3
"""Validate fixture layout, metadata completeness, contract mapping, and export derivation."""
from __future__ import annotations

import json
import pathlib
import sys
from collections import Counter
from typing import Any

DATASET_VERSION_PATH = pathlib.Path("DATASET_VERSION")
DATASET_MAPPING_PATH = pathlib.Path("DATASET_ENGINE_MAPPING.json")
REQUIRED_METADATA_FIELDS = (
    "fixture_id",
    "model_version",
    "contract_version",
    "policy_pack_id",
    "policy_pack_version",
    "profile_id",
    "profile_version",
    "device",
    "scenario_type",
    "expected_outcome",
)
REQUIRED_SCENARIO_TYPES = {
    "baseline_pass",
    "drift_guard",
    "infeasible_request",
    "missing_inputs",
    "minimal_delta_patch",
    "multi_file_artifact",
    "patch_bundle",
    "patch_conflict",
    "validator_failure",
    "validator_pack",
    "policy_pack_aware",
    "profile_aware",
    "compatibility_legacy",
}
REQUIRED_OUTCOMES = {"pass", "fail", "infeasible"}


def load_json(path: pathlib.Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc


def get_dataset_version() -> str:
    if not DATASET_VERSION_PATH.exists():
        raise SystemExit("DATASET_VERSION file missing.")
    return DATASET_VERSION_PATH.read_text(encoding="utf-8").strip()


def get_mapping(dataset_version: str) -> dict[str, Any]:
    if not DATASET_MAPPING_PATH.exists():
        raise SystemExit("DATASET_ENGINE_MAPPING.json file missing.")
    mapping = load_json(DATASET_MAPPING_PATH)
    if mapping.get("dataset_version") != dataset_version:
        raise SystemExit(
            "DATASET_ENGINE_MAPPING.json does not match DATASET_VERSION: "
            f"{mapping.get('dataset_version')} != {dataset_version}"
        )
    return mapping


def expect_version(path: pathlib.Path, expected: str, errors: list[str]) -> Any:
    data = load_json(path)
    version = data.get("version")
    if version != expected:
        errors.append(f"Version mismatch in {path}: expected {expected}, got {version}")
    return data


def validate_goal_metadata(goal_path: pathlib.Path, mapping: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    dataset_version = mapping["dataset_version"]
    goal = expect_version(goal_path, dataset_version, errors)
    metadata = goal.get("metadata")
    if not isinstance(metadata, dict):
        errors.append(f"Missing metadata object in {goal_path}")
        return {}

    missing = [field for field in REQUIRED_METADATA_FIELDS if field not in metadata]
    if missing:
        errors.append(f"Missing metadata fields in {goal_path}: {', '.join(missing)}")

    if metadata.get("fixture_id") != goal_path.parent.name:
        errors.append(
            f"fixture_id mismatch in {goal_path}: expected {goal_path.parent.name}, got {metadata.get('fixture_id')}"
        )
    if metadata.get("model_version") != mapping["engine_line"]:
        errors.append(
            f"model_version mismatch in {goal_path}: expected {mapping['engine_line']}, got {metadata.get('model_version')}"
        )
    if metadata.get("contract_version") != mapping["fixture_contract_version"]:
        errors.append(
            f"contract_version mismatch in {goal_path}: expected {mapping['fixture_contract_version']}, got {metadata.get('contract_version')}"
        )
    if metadata.get("expected_outcome") not in REQUIRED_OUTCOMES:
        errors.append(f"Invalid expected_outcome in {goal_path}: {metadata.get('expected_outcome')}")
    if not metadata.get("scenario_type"):
        errors.append(f"Missing scenario_type in {goal_path}")

    return metadata


def enumerate_expected_dirs(expected_root: pathlib.Path) -> list[tuple[pathlib.Path, str, str | None]]:
    bundles: list[tuple[pathlib.Path, str, str | None]] = []
    for entry in sorted(expected_root.iterdir()):
        if not entry.is_dir():
            continue
        if (entry / "expected_artifact.json").exists() or (entry / "expected_verdict.json").exists():
            bundles.append((entry, entry.name, None))
            continue
        for pack_dir in sorted(entry.iterdir()):
            if pack_dir.is_dir():
                bundles.append((pack_dir, pack_dir.name, entry.name))
    return bundles


def validate_request_block(payload: dict[str, Any], goal_metadata: dict[str, Any], errors: list[str], path: pathlib.Path) -> None:
    request = payload.get("request")
    if not isinstance(request, dict):
        errors.append(f"Missing request object in {path}")
        return
    for key in ("policy_pack_id", "policy_pack_version", "profile_id", "profile_version", "device"):
        if key not in request:
            errors.append(f"Missing request.{key} in {path}")
    if not isinstance(payload.get("engine"), dict):
        errors.append(f"Missing engine object in {path}")
        return
    engine = payload["engine"]
    for key in ("name", "line", "dataset_version"):
        if key not in engine:
            errors.append(f"Missing engine.{key} in {path}")
    if payload.get("fixture_id") != goal_metadata.get("fixture_id"):
        errors.append(f"fixture_id mismatch in {path}")


def derive_export_row(
    fixture_dir: pathlib.Path,
    bundle_dir: pathlib.Path,
    goal_metadata: dict[str, Any],
    dataset_version: str,
    *,
    policy_pack_id: str,
    profile_id: str | None,
    archive_version: str | None = None,
) -> dict[str, Any]:
    metadata = dict(goal_metadata)
    metadata["model_version"] = archive_version or dataset_version
    metadata["policy_pack_id"] = policy_pack_id
    metadata["profile_id"] = profile_id or goal_metadata.get("profile_id")
    metadata["archive_version"] = archive_version
    report_path = bundle_dir / "report.json"
    return {
        "input": {"path": str((fixture_dir / "goal.json").as_posix())},
        "artifact": {"path": str((bundle_dir / "expected_artifact.json").as_posix())},
        "verdict": {"path": str((bundle_dir / "expected_verdict.json").as_posix())},
        "report": {"path": str(report_path.as_posix())} if report_path.exists() else None,
        "metadata": metadata,
    }


def validate_fixture(fixture_dir: pathlib.Path, mapping: dict[str, Any], coverage: Counter[str]) -> list[str]:
    errors: list[str] = []
    goal = fixture_dir / "goal.json"
    if not goal.exists():
        errors.append(f"Missing {goal}")
        return errors

    goal_metadata = validate_goal_metadata(goal, mapping, errors)
    scenario_type = goal_metadata.get("scenario_type")
    if scenario_type:
        coverage[scenario_type] += 1
    outcome = goal_metadata.get("expected_outcome")
    if outcome:
        coverage[f"outcome:{outcome}"] += 1

    expected_root = fixture_dir / "expected" / mapping["dataset_version"]
    if not expected_root.exists():
        errors.append(f"Missing expected outputs for {fixture_dir.name}: {expected_root}")
        return errors

    bundles = enumerate_expected_dirs(expected_root)
    if not bundles:
        errors.append(f"No expectation bundles found in {expected_root}.")
        return errors

    for bundle_dir, policy_pack_id, profile_id in bundles:
        artifact_path = bundle_dir / "expected_artifact.json"
        verdict_path = bundle_dir / "expected_verdict.json"
        for path in (artifact_path, verdict_path):
            if not path.exists():
                errors.append(f"Missing {path}")
        if not artifact_path.exists() or not verdict_path.exists():
            continue

        artifact = expect_version(artifact_path, mapping["dataset_version"], errors)
        verdict = expect_version(verdict_path, mapping["dataset_version"], errors)
        validate_request_block(artifact, goal_metadata, errors, artifact_path)
        validate_request_block(verdict, goal_metadata, errors, verdict_path)
        if artifact.get("contract_version") != mapping["output_contract_version"]:
            errors.append(f"Artifact contract mismatch in {artifact_path}")
        if verdict.get("contract_version") != mapping["output_contract_version"]:
            errors.append(f"Verdict contract mismatch in {verdict_path}")
        if verdict.get("status") != verdict.get("outcome"):
            errors.append(f"Verdict status/outcome mismatch in {verdict_path}")
        report = bundle_dir / "report.json"
        if report.exists():
            report_data = expect_version(report, mapping["dataset_version"], errors)
            validate_request_block(report_data, goal_metadata, errors, report)
            if report_data.get("contract_version") != mapping["report_contract_version"]:
                errors.append(f"Report contract mismatch in {report}")
            if report_data.get("status") != report_data.get("outcome"):
                errors.append(f"Report status/outcome mismatch in {report}")
            coverage["report_harness"] += 1

        row = derive_export_row(
            fixture_dir,
            bundle_dir,
            goal_metadata,
            mapping["dataset_version"],
            policy_pack_id=policy_pack_id,
            profile_id=profile_id,
        )
        for section in ("input", "artifact", "verdict"):
            path = pathlib.Path(row[section]["path"])
            if not path.exists():
                errors.append(f"Export row points to missing path: {path}")
        if row["report"] is not None and not pathlib.Path(row["report"]["path"]).exists():
            errors.append(f"Export row points to missing report path: {row['report']['path']}")
        if verdict.get("outcome") != row["metadata"]["expected_outcome"] and fixture_dir.name != "policy_pack_matrix":
            errors.append(
                f"Expected outcome mismatch for {fixture_dir.name} bundle {bundle_dir}: "
                f"goal metadata says {row['metadata']['expected_outcome']}, verdict says {verdict.get('outcome')}"
            )
        if profile_id is not None:
            coverage["profile_aware"] += 1
        if policy_pack_id != "default":
            coverage["policy_pack_variant"] += 1

    archive_root = fixture_dir / "archives"
    if archive_root.exists():
        coverage["compatibility_legacy"] += 1
        for version_dir in sorted(archive_root.iterdir()):
            if not version_dir.is_dir():
                continue
            for pack_dir in sorted(version_dir.iterdir()):
                if not pack_dir.is_dir():
                    continue
                for name in ("expected_artifact.json", "expected_verdict.json"):
                    path = pack_dir / name
                    if not path.exists():
                        errors.append(f"Missing {path}")
                        continue
                    data = expect_version(path, version_dir.name, errors)
                    validate_request_block(data, goal_metadata, errors, path)
                derive_export_row(
                    fixture_dir,
                    pack_dir,
                    goal_metadata,
                    mapping["dataset_version"],
                    policy_pack_id=pack_dir.name,
                    profile_id=None,
                    archive_version=version_dir.name,
                )

    return errors


def main() -> int:
    dataset_version = get_dataset_version()
    mapping = get_mapping(dataset_version)
    fixture_root = pathlib.Path("fixtures")
    if not fixture_root.exists():
        raise SystemExit("fixtures directory missing.")

    failures: list[str] = []
    coverage: Counter[str] = Counter()
    for fixture_dir in sorted(p for p in fixture_root.iterdir() if p.is_dir()):
        failures.extend(validate_fixture(fixture_dir, mapping, coverage))

    for required in REQUIRED_SCENARIO_TYPES:
        if coverage[required] == 0:
            failures.append(f"Coverage gap: missing scenario_type '{required}'")
    for required in REQUIRED_OUTCOMES:
        if coverage[f"outcome:{required}"] == 0:
            failures.append(f"Coverage gap: missing outcome '{required}'")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print(
        "Fixture layout, metadata completeness, engine mapping, and export derivation validated."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
