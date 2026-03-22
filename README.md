# blux-ca-dataset

Deterministic fixtures and regression cases for `blux-ca`.

## Dataset charter
- This repo detects engine drift; it does not define `blux-ca` behavior.
- `cA V1.0 Dataset` maps to the engine line `cA-1.0-pro`.
- `cA-1.0` and earlier lines remain archived only for compatibility checks in `fixtures/*/archives/`.
- Fixtures are deterministic and versioned for reproducibility.
- Update fixtures only when the real engine changes or when the dataset contract is intentionally refined.
- Current dataset version: `cA-1.0-pro` (see `DATASET_VERSION`).

## Structure
- `schemas/` — JSON Schemas for fixture goals, expected artifacts, expected verdicts, and export rows.
- `fixtures/` — Deterministic fixture bundles aligned to the `cA-1.0-pro` engine line.
- `scripts/verify_fixtures.py` — Compares canonical JSON bytes to expected outputs.
- `scripts/validate_dataset.py` — Validates fixture layout, metadata completeness, category coverage, and export derivation.
- `docs/` — Policy and platform notes.
- `DATASET_VERSION` — Current dataset version.

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
          report.json            # optional
        <profile_id>/            # optional profile-specific expectations
          <policy_pack_id>/
            expected_artifact.json
            expected_verdict.json
            report.json          # optional
    archives/                    # optional compatibility expectations
      <legacy_version>/
        <policy_pack_id>/
          expected_artifact.json
          expected_verdict.json
          report.json            # optional
```

## Export-ready contract
Each expectation bundle deterministically maps to one later export row:
- `input` → `fixtures/<case>/goal.json`
- `artifact` → `expected_artifact.json`
- `verdict` → `expected_verdict.json`
- `metadata` → derived from `goal.json.metadata` plus the explicit model version, policy pack, profile, and archive lineage encoded by the fixture path

The row shape is defined in `schemas/export_row.schema.json`. The repo intentionally stops at the validated source structure; it does not generate JSONL in this repo.

## Coverage in the corpus
The repo currently covers these non-redundant categories:
- PASS cases: `hello`, `multi_file_artifact`, `patch_bundle`, `minimal_delta`, `validator_pack`, `policy_pack_matrix` (`cA-pro`), `profile_echo`, `legacy_outputs`
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
- Harness / report-aware: all fixtures that carry `report.json`

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

Expectation paths may override or specialize the default metadata through their path components, for example `cA-mini` or `cpu/cA-pro`.

## Updating fixtures truthfully
1. Confirm the real `blux-ca` engine behavior first.
2. Regenerate only the fixtures whose outputs intentionally changed.
3. Remove stale or aspirational expectations instead of preserving them as “future” behavior.
4. Keep version mapping explicit: `cA V1.0 Dataset` = `cA-1.0-pro`.
5. Run both validation and verification before merging.

See `docs/POLICY.md` for governance details and `docs/PLATFORMS.md` for environment setup.
