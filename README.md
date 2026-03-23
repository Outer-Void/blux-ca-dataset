# blux-ca-dataset

Deterministic fixtures, regression cases, and export material for `blux-ca`.

## Dataset charter
- This repo detects drift in the real `blux-ca` engine; it does **not** define engine behavior.
- The active frozen dataset line is `cA V1.0 Dataset`.
- `cA V1.0 Dataset` maps directly to the `blux-ca` engine line `cA-1.0-pro`.
- The authoritative version freeze record is `DATASET_ENGINE_MAPPING.json`.
- `cA-1.0` and earlier lines remain archived only for compatibility checks in `fixtures/*/archives/`.
- Fixture updates are allowed only when the live engine changes, or when stored expectations are missing real stable engine contract fields.
- Current active dataset version: `cA-1.0-pro` from `DATASET_VERSION`.

## Structure
- `schemas/` — JSON Schemas for fixture goals, engine-aligned expected artifacts/verdicts/reports, and export rows.
- `fixtures/` — deterministic fixture bundles aligned to the `cA-1.0-pro` engine line.
- `scripts/validate_dataset.py` — validates fixture layout, metadata completeness, version mapping, and export derivation.
- `scripts/verify_fixtures.py` — verifies expected outputs against a captured dataset-format run directory or against a real local `blux-ca` checkout using the supported `accept` CLI.
- `scripts/export_jsonl.py` — emits a deterministic JSONL export for GitHub freeze and HuggingFace handoff.
- `exports/` — generated deterministic JSONL artifacts and checksums.
- `docs/` — policy, platform, verification, and export notes.

## Dataset-to-engine version freeze
| Dataset field | Frozen value |
| --- | --- |
| Dataset ID | `cA V1.0 Dataset` |
| Dataset repo | `blux-ca-dataset` |
| Dataset version | `cA-1.0-pro` |
| Engine name | `blux-ca` |
| Engine line | `cA-1.0-pro` |
| Fixture contract | `fixture-contract-1.1` |
| Output contract | `blux-ca-output-1.1` |
| Report contract | `blux-ca-report-1.1` |
| Export contract | `blux-ca-export-row-1.2` |
| Mapping date | `2026-03-22` |

## Fixture layout
```text
fixtures/
  <case>/
    goal.json
    expected/
      <model_version>/
        <policy_pack_id>/
          expected_artifact.json
          expected_verdict.json
          report.json            # optional but preferred for harness-aware cases
        <profile_id>/            # optional profile-specific expectations
          <policy_pack_id>/
            expected_artifact.json
            expected_verdict.json
            report.json
    archives/
      <legacy_version>/
        <policy_pack_id>/
          expected_artifact.json
          expected_verdict.json
          report.json
```

## Engine-aligned expected contract
Expected outputs mirror the stable engine envelope rather than simplified placeholder fragments.

### `expected_artifact.json`
- `version`
- `contract_version`
- `fixture_id`
- `engine`
- `request`
- `artifact`
- `artifact_kind`
- `mime_type`

### `expected_verdict.json`
- `version`
- `contract_version`
- `fixture_id`
- `engine`
- `request`
- `status`
- `outcome`
- `summary`
- `notes`
- `drift_status`

### `report.json`
- dataset-side verification bridge metadata stored per fixture bundle
- retains stable dataset mapping fields: `version`, `contract_version`, `fixture_id`, `engine`, and `request`
- records `mode`, `status`, `outcome`, and deterministic `checks` used by this repo's validation/export pipeline
- live `blux-ca` emits a top-level acceptance `report.json`; `scripts/verify_fixtures.py` bridges that real report back to these fixture-local expectations truthfully

## Coverage in the corpus
The current non-redundant coverage includes:
- PASS: `hello`, `multi_file_artifact`, `patch_bundle`, `minimal_delta`, `validator_pack`, `policy_pack_matrix` (`cA-pro`), `profile_echo`, `legacy_outputs`, `drift_probe`
- FAIL: `conflict_detection`, `duplicate_paths`, `path_traversal`, `unsorted_output`, `policy_pack_matrix` (`cA-mini`)
- INFEASIBLE: `infeasible`, `missing_inputs`
- Drift guard: `drift_probe`
- Validator failures: `duplicate_paths`, `path_traversal`, `unsorted_output`
- Multi-file artifacts: `multi_file_artifact`
- Patch bundles: `patch_bundle`, `minimal_delta`
- Minimal delta: `minimal_delta`
- Policy-pack aware: `policy_pack_matrix`
- Profile-aware: `profile_echo`
- Compatibility / legacy: `legacy_outputs`
- Harness / report-aware: fixtures carrying `report.json`

## Metadata requirements
Each fixture goal includes metadata needed for verification and export:
- `fixture_id`
- `model_version`
- `contract_version`
- `policy_pack_id`
- `policy_pack_version`
- `profile_id`
- `profile_version`
- `device`
- `scenario_type`
- `expected_outcome`

Expectation path components may specialize `policy_pack_id`, `profile_id`, and archived `model_version` per bundle.

## Canonical validation, verification, and export flow
```bash
python scripts/validate_dataset.py
python scripts/verify_fixtures.py --actual-root <captured-dataset-format-runs> --policy-pack cA-pro
python scripts/export_jsonl.py --include-archives --write-sha256
```

For direct verification against a real local `blux-ca` checkout, point the verifier at the repo root:
```bash
python scripts/verify_fixtures.py --engine-root /workspace/blux-ca --policy-pack cA-pro
python scripts/verify_fixtures.py --engine-root /workspace/blux-ca --policy-pack cA-mini
python scripts/verify_fixtures.py --engine-root /workspace/blux-ca --policy-pack cA-pro --profile cpu
```

`verify_fixtures.py` generates engine-compatible temporary fixture goals and invokes the real supported CLI:
`python -m blux_ca accept --fixtures <generated-bridge-dir> --out <temp-run-dir> [--profile <id>]`.
It does **not** assume unsupported engine flags such as `--policy-pack` or `--out-dir`.

## Export contract
Each JSONL row is stable, ordered, and reproducible. It includes:
- `source_paths` for traceability back to the repo
- `input` with full `goal.json` content
- `artifact` with the full expected engine artifact envelope
- `verdict` with the full expected engine verdict envelope
- `report` when present
- `metadata` with dataset freeze fields, policy/profile lineage, archive lineage, and export flags

This makes the repository ready for deterministic HuggingFace dataset publication and later training-data derivation.

See `docs/POLICY.md`, `docs/PLATFORMS.md`, `docs/VERIFICATION.md`, and `docs/EXPORT.md` for operational details.
