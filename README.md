# blux-ca-dataset

Deterministic fixtures and regression cases for `blux-ca`.

## Dataset charter
- This repo detects engine drift; it does not define `blux-ca` behavior.
- The active dataset line is `cA V1.0 Dataset`.
- `cA V1.0 Dataset` maps directly to the live local `blux-ca` engine line `cA-1.0-pro`.
- The authoritative mapping file is `DATASET_ENGINE_MAPPING.json`.
- `cA-1.0` and earlier lines remain archived only for compatibility checks in `fixtures/*/archives/`.
- Fixtures are deterministic and versioned for reproducibility.
- Update fixtures only when the real engine changes or when the stored dataset contract is incomplete or misleading.
- Current dataset version: `cA-1.0-pro` (see `DATASET_VERSION`).

## Structure
- `schemas/` — JSON Schemas for fixture goals, expected artifacts, expected verdicts, expected reports, and export rows.
- `fixtures/` — Deterministic fixture bundles aligned to the `cA-1.0-pro` engine line.
- `scripts/verify_fixtures.py` — Verifies fixture outputs against the real local engine command or a captured run directory.
- `scripts/validate_dataset.py` — Validates fixture layout, metadata completeness, contract mapping, coverage, and export derivation.
- `docs/` — Policy and platform notes.
- `DATASET_VERSION` — Current dataset version.
- `DATASET_ENGINE_MAPPING.json` — Explicit dataset-to-engine mapping and contract versions.

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

## Expected contract shape
Expected outputs now mirror the engine envelope instead of only storing abstract payload fragments.

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
- `version`
- `contract_version`
- `fixture_id`
- `engine`
- `request`
- `mode`
- `status`
- `outcome`
- `checks`
- optional pack/profile/report annotations when the engine emits them

## Export-ready contract
Each expectation bundle deterministically maps to one later export row:
- `input` → `fixtures/<case>/goal.json`
- `artifact` → `expected_artifact.json`
- `verdict` → `expected_verdict.json`
- `report` → optional `report.json`
- `metadata` → derived from `goal.json.metadata` plus the explicit model version, policy pack, profile, and archive lineage encoded by the fixture path

The row shape is defined in `schemas/export_row.schema.json`. This repo is intentionally export-ready but does not ship a fake JSONL exporter.

## Coverage in the corpus
The current non-redundant coverage is:
- PASS cases: `hello`, `multi_file_artifact`, `patch_bundle`, `minimal_delta`, `validator_pack`, `policy_pack_matrix` (`cA-pro`), `profile_echo`, `legacy_outputs`, `drift_probe`
- FAIL cases: `conflict_detection`, `duplicate_paths`, `path_traversal`, `unsorted_output`, `policy_pack_matrix` (`cA-mini`)
- INFEASIBLE cases: `infeasible`, `missing_inputs`
- Drift guard: `drift_probe`
- Validator failures: `duplicate_paths`, `path_traversal`, `unsorted_output`
- Multi-file outputs: `multi_file_artifact`
- Patch bundles: `patch_bundle`, `minimal_delta`
- Minimal delta: `minimal_delta`
- Policy-pack aware: `policy_pack_matrix`
- Profile-aware: `profile_echo`
- Compatibility / legacy: `legacy_outputs`
- Harness / report-aware: every fixture that carries `report.json`

## Fixture metadata requirements
Each `goal.json` includes `metadata` fields for export derivation:
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

Expectation paths may override or specialize default metadata through their path components, for example `cA-mini` or `cpu/cA-pro`.

## Updating fixtures truthfully
1. Confirm the current local `blux-ca` engine behavior first.
2. Refresh only the fixtures whose engine outputs changed.
3. Update expectations, schemas, scripts, and docs in the same pass whenever the engine contract changes.
4. Remove stale or aspirational expectations instead of preserving them as “future” behavior.
5. Preserve old accepted outputs only in `archives/` when compatibility history matters.
6. Run both validation and verification before merging.

See `docs/POLICY.md` for governance details and `docs/PLATFORMS.md` for environment setup.
