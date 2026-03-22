#!/usr/bin/env python3
"""Shared helpers for BLUX cA dataset validation, export, and verification."""
from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass
from typing import Any, Iterable

DATASET_VERSION_PATH = pathlib.Path("DATASET_VERSION")
DATASET_MAPPING_PATH = pathlib.Path("DATASET_ENGINE_MAPPING.json")
FIXTURE_ROOT = pathlib.Path("fixtures")
VOLATILE_KEYS = {"generated_at", "started_at", "completed_at", "run_id", "trace_id", "duration_ms"}
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


def load_json(path: pathlib.Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc



def read_dataset_version() -> str:
    if not DATASET_VERSION_PATH.exists():
        raise SystemExit("DATASET_VERSION file missing.")
    return DATASET_VERSION_PATH.read_text(encoding="utf-8").strip()



def read_mapping() -> dict[str, Any]:
    dataset_version = read_dataset_version()
    if not DATASET_MAPPING_PATH.exists():
        raise SystemExit("DATASET_ENGINE_MAPPING.json file missing.")
    mapping = load_json(DATASET_MAPPING_PATH)
    if mapping.get("dataset_version") != dataset_version:
        raise SystemExit(
            "DATASET_ENGINE_MAPPING.json does not match DATASET_VERSION: "
            f"{mapping.get('dataset_version')} != {dataset_version}"
        )
    return mapping



def normalize(payload: Any) -> Any:
    if isinstance(payload, dict):
        return {k: normalize(v) for k, v in sorted(payload.items()) if k not in VOLATILE_KEYS}
    if isinstance(payload, list):
        return [normalize(v) for v in payload]
    return payload



def canonical_dumps(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)



def fixture_dirs(root: pathlib.Path = FIXTURE_ROOT) -> list[pathlib.Path]:
    if not root.exists():
        raise SystemExit(f"fixtures directory missing: {root}")
    return sorted(path for path in root.iterdir() if path.is_dir())


@dataclass(frozen=True)
class BundleRef:
    fixture_dir: pathlib.Path
    bundle_dir: pathlib.Path
    model_version: str
    policy_pack_id: str
    profile_id: str | None
    archive_version: str | None



def iter_expected_bundles(
    fixture_dir: pathlib.Path,
    dataset_version: str,
) -> Iterable[BundleRef]:
    expected_root = fixture_dir / "expected" / dataset_version
    if expected_root.exists():
        for entry in sorted(expected_root.iterdir()):
            if not entry.is_dir():
                continue
            if (entry / "expected_artifact.json").exists() or (entry / "expected_verdict.json").exists():
                yield BundleRef(fixture_dir, entry, dataset_version, entry.name, None, None)
                continue
            for pack_dir in sorted(path for path in entry.iterdir() if path.is_dir()):
                yield BundleRef(fixture_dir, pack_dir, dataset_version, pack_dir.name, entry.name, None)

    archive_root = fixture_dir / "archives"
    if archive_root.exists():
        for version_dir in sorted(path for path in archive_root.iterdir() if path.is_dir()):
            for pack_dir in sorted(path for path in version_dir.iterdir() if path.is_dir()):
                yield BundleRef(fixture_dir, pack_dir, version_dir.name, pack_dir.name, None, version_dir.name)



def build_export_row(bundle: BundleRef, mapping: dict[str, Any]) -> dict[str, Any]:
    goal_path = bundle.fixture_dir / "goal.json"
    goal = normalize(load_json(goal_path))
    artifact_path = bundle.bundle_dir / "expected_artifact.json"
    verdict_path = bundle.bundle_dir / "expected_verdict.json"
    report_path = bundle.bundle_dir / "report.json"
    artifact = normalize(load_json(artifact_path))
    verdict = normalize(load_json(verdict_path))
    report = normalize(load_json(report_path)) if report_path.exists() else None

    goal_metadata = dict(goal.get("metadata") or {})
    request = dict(verdict.get("request") or artifact.get("request") or {})
    engine = dict(verdict.get("engine") or artifact.get("engine") or {})

    metadata = {
        "dataset_id": mapping["dataset_id"],
        "dataset_repo": mapping["dataset_repo"],
        "dataset_version": mapping["dataset_version"],
        "engine_name": mapping["engine_name"],
        "engine_line": mapping["engine_line"],
        "fixture_id": goal_metadata.get("fixture_id", bundle.fixture_dir.name),
        "model_version": bundle.model_version,
        "contract_version": goal_metadata.get("contract_version"),
        "output_contract_version": artifact.get("contract_version"),
        "report_contract_version": report.get("contract_version") if report else None,
        "policy_pack_id": request.get("policy_pack_id", bundle.policy_pack_id),
        "policy_pack_version": request.get("policy_pack_version"),
        "profile_id": request.get("profile_id", bundle.profile_id or goal_metadata.get("profile_id")),
        "profile_version": request.get("profile_version", goal_metadata.get("profile_version")),
        "device": request.get("device", goal_metadata.get("device")),
        "scenario_type": goal_metadata.get("scenario_type"),
        "expected_outcome": verdict.get("outcome", goal_metadata.get("expected_outcome")),
        "archive_version": bundle.archive_version,
        "has_report": report is not None,
        "source_kind": "archive" if bundle.archive_version else "expected",
    }

    return {
        "source_paths": {
            "goal": goal_path.as_posix(),
            "artifact": artifact_path.as_posix(),
            "verdict": verdict_path.as_posix(),
            "report": report_path.as_posix() if report_path.exists() else None,
        },
        "input": goal,
        "artifact": artifact,
        "verdict": verdict,
        "report": report,
        "metadata": metadata,
    }
