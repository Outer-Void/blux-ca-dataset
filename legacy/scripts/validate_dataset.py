#!/usr/bin/env python3
"""Validate fixture layout, metadata completeness, contract mapping, and export derivation."""
from __future__ import annotations

import pathlib
import sys
from collections import Counter
from typing import Any

from dataset_common import (
    REQUIRED_METADATA_FIELDS,
    build_export_row,
    fixture_dirs,
    iter_expected_bundles,
    load_json,
    read_mapping,
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



def validate_request_block(
    payload: dict[str, Any],
    goal_metadata: dict[str, Any],
    mapping: dict[str, Any],
    errors: list[str],
    path: pathlib.Path,
    *,
    expected_policy_pack_id: str,
    expected_profile_id: str | None,
    expected_model_version: str,
) -> None:
    request = payload.get("request")
    if not isinstance(request, dict):
        errors.append(f"Missing request object in {path}")
        return
    for key in ("policy_pack_id", "policy_pack_version", "profile_id", "profile_version", "device"):
        if key not in request:
            errors.append(f"Missing request.{key} in {path}")
    if request.get("policy_pack_id") != expected_policy_pack_id:
        errors.append(
            f"request.policy_pack_id mismatch in {path}: expected {expected_policy_pack_id}, got {request.get('policy_pack_id')}"
        )
    if expected_profile_id is not None and request.get("profile_id") != expected_profile_id:
        errors.append(
            f"request.profile_id mismatch in {path}: expected {expected_profile_id}, got {request.get('profile_id')}"
        )
    if expected_profile_id is None and request.get("profile_id") != goal_metadata.get("profile_id"):
        errors.append(
            f"request.profile_id mismatch in {path}: expected {goal_metadata.get('profile_id')}, got {request.get('profile_id')}"
        )
    if not isinstance(payload.get("engine"), dict):
        errors.append(f"Missing engine object in {path}")
        return
    engine = payload["engine"]
    for key in ("name", "line", "dataset_version"):
        if key not in engine:
            errors.append(f"Missing engine.{key} in {path}")
    if engine.get("name") != mapping["engine_name"]:
        errors.append(f"engine.name mismatch in {path}: expected {mapping['engine_name']}, got {engine.get('name')}")
    if engine.get("line") != expected_model_version:
        errors.append(f"engine.line mismatch in {path}: expected {expected_model_version}, got {engine.get('line')}")
    if engine.get("dataset_version") != mapping["dataset_version"]:
        errors.append(
            f"engine.dataset_version mismatch in {path}: expected {mapping['dataset_version']}, got {engine.get('dataset_version')}"
        )
    if payload.get("fixture_id") != goal_metadata.get("fixture_id"):
        errors.append(f"fixture_id mismatch in {path}")



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

    bundles = list(iter_expected_bundles(fixture_dir, mapping["dataset_version"]))
    if not bundles:
        errors.append(f"No expectation bundles found for {fixture_dir.name}.")
        return errors

    for bundle in bundles:
        artifact_path = bundle.bundle_dir / "expected_artifact.json"
        verdict_path = bundle.bundle_dir / "expected_verdict.json"
        for path in (artifact_path, verdict_path):
            if not path.exists():
                errors.append(f"Missing {path}")
        if not artifact_path.exists() or not verdict_path.exists():
            continue

        artifact = expect_version(artifact_path, bundle.model_version, errors)
        verdict = expect_version(verdict_path, bundle.model_version, errors)
        validate_request_block(
            artifact,
            goal_metadata,
            mapping,
            errors,
            artifact_path,
            expected_policy_pack_id=bundle.policy_pack_id,
            expected_profile_id=bundle.profile_id,
            expected_model_version=bundle.model_version,
        )
        validate_request_block(
            verdict,
            goal_metadata,
            mapping,
            errors,
            verdict_path,
            expected_policy_pack_id=bundle.policy_pack_id,
            expected_profile_id=bundle.profile_id,
            expected_model_version=bundle.model_version,
        )
        if artifact.get("contract_version") != mapping["output_contract_version"]:
            errors.append(f"Artifact contract mismatch in {artifact_path}")
        if verdict.get("contract_version") != mapping["output_contract_version"]:
            errors.append(f"Verdict contract mismatch in {verdict_path}")
        if verdict.get("status") != verdict.get("outcome"):
            errors.append(f"Verdict status/outcome mismatch in {verdict_path}")
        report = bundle.bundle_dir / "report.json"
        if report.exists():
            report_data = expect_version(report, bundle.model_version, errors)
            validate_request_block(
                report_data,
                goal_metadata,
                mapping,
                errors,
                report,
                expected_policy_pack_id=bundle.policy_pack_id,
                expected_profile_id=bundle.profile_id,
                expected_model_version=bundle.model_version,
            )
            if report_data.get("contract_version") != mapping["report_contract_version"]:
                errors.append(f"Report contract mismatch in {report}")
            if report_data.get("status") != report_data.get("outcome"):
                errors.append(f"Report status/outcome mismatch in {report}")
            coverage["report_harness"] += 1

        row = build_export_row(bundle, mapping)
        for section in ("goal", "artifact", "verdict"):
            path = pathlib.Path(row["source_paths"][section])
            if not path.exists():
                errors.append(f"Export row points to missing path: {path}")
        if row["source_paths"]["report"] is not None and not pathlib.Path(row["source_paths"]["report"]).exists():
            errors.append(f"Export row points to missing report path: {row['source_paths']['report']}")
        if bundle.archive_version is None and bundle.fixture_dir.name != "policy_pack_matrix":
            if verdict.get("outcome") != row["metadata"]["expected_outcome"]:
                errors.append(
                    f"Expected outcome mismatch for {fixture_dir.name} bundle {bundle.bundle_dir}: "
                    f"goal metadata says {row['metadata']['expected_outcome']}, verdict says {verdict.get('outcome')}"
                )
        if bundle.profile_id is not None:
            coverage["profile_aware"] += 1
        if bundle.policy_pack_id != "default":
            coverage["policy_pack_variant"] += 1
        if bundle.archive_version is not None:
            coverage["compatibility_legacy"] += 1

    return errors



def main() -> int:
    mapping = read_mapping()
    failures: list[str] = []
    coverage: Counter[str] = Counter()
    for fixture_dir in fixture_dirs():
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

    print("Fixture layout, metadata completeness, engine mapping, and export derivation validated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
