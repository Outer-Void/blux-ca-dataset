# blux-ca-dataset

Deterministic fixtures and regression cases for `blux-ca`.

## Dataset charter
- Datasets detect drift; they do not define behavior.
- Fixtures are deterministic and versioned for reproducibility.
- Update fixtures only with deliberate version bumps.
- Phase 1 provides schema + minimal fixtures and a tiny verifier.
- Current dataset version: `cA-1.0` (see `DATASET_VERSION`).

## Structure (Phases 1-10)
- `schemas/` — JSON Schemas for goals, expected artifacts, and expected verdicts.
- `fixtures/` — Deterministic fixture bundles through cA V1.0 (Phase 1-10).
- `scripts/verify_fixtures.py` — Compares canonical JSON bytes to expected outputs.
- `scripts/validate_dataset.py` — Ensures fixture layout + version consistency.
- `docs/` — Contributor notes and platform setup.
- `DATASET_VERSION` — Current dataset version (bump when fixtures change).

## Fixture layout
```
fixtures/
  <case>/
    goal.json
    expected/
      <model_version>/
        <policy_pack_id>/        # default expectations
          expected_artifact.json
          expected_verdict.json
          report.json            # optional
        <profile_id>/            # profile-specific expectations (optional)
          expected_artifact.json
          expected_verdict.json
          report.json            # optional
          <policy_pack_id>/      # optional policy-pack subfolder
            expected_artifact.json
            expected_verdict.json
            report.json          # optional
    archives/                   # optional
      <legacy_version>/
        <policy_pack_id>/
          expected_artifact.json
          expected_verdict.json
          report.json            # optional
```

## Phase 3 fixtures (structural bundles)
- `multi_file_artifact` — Multi-file artifact with canonical ordering.
- `patch_bundle` — Patch bundle with ordered, unified diffs.
- `path_traversal` — Failure case for disallowed `../` paths.
- `duplicate_paths` — Failure case for repeated file paths.
- `unsorted_output` — Failure case for unsorted file listings.

## Phase 4+ acceptance harness
Acceptance mode reads `report.json` alongside expected artifacts/verdicts to capture
the harness verdict for structural checks. When running in acceptance mode, emit a
`report.json` per fixture under your run root (e.g., `runs/multi_file_artifact/report.json`)
and compare it to the fixture's `report.json` if present.

## Policy pack coverage (Phase 5)
Fixtures can be run under different policy packs. Store expectations per pack at:
`fixtures/<case>/expected/<model_version>/<policy_pack_id>/`.

## Profile-aware expectations (Option A)
When fixture behavior varies by profile, add a profile-specific expectation bundle
under `fixtures/<case>/expected/<model_version>/<profile_id>/` and keep the default
expectations untouched. Use `goal.json` metadata fields such as `required_profile_id`,
`required_profile_version`, and `device` to describe required runtime context. Avoid
duplicating outputs unless the profile changes behavior.

## Compatibility coverage (Phase 7)
Legacy outputs live under `fixtures/<case>/archives/<legacy_version>/<policy_pack_id>/`
and are compared when validating older outputs.

## Verifying outputs
1) Run cA for each `goal.json` and store the outputs under a directory, one folder per
   fixture:
   ```
   runs/
     hello/
       artifact.json
       verdict.json
       report.json
     infeasible/
       artifact.json
       verdict.json
       report.json
     drift_probe/
       artifact.json
       verdict.json
       report.json
   ```
2) Compare canonical JSON bytes against expectations:
   ```bash
   ./scripts/verify_fixtures.py --actual-root runs --policy-pack default
   ```
   To compare profile-aware expectations, add `--profile`:
   ```bash
   ./scripts/verify_fixtures.py --actual-root runs --policy-pack default --profile <profile_id>
   ```
3) Validate fixture layout + dataset versioning:
   ```bash
   ./scripts/validate_dataset.py
   ```

To compare legacy outputs, store them under `runs/archives/<legacy_version>/<policy_pack>/<fixture>/`
and invoke:
```bash
./scripts/verify_fixtures.py --actual-root runs --policy-pack default --include-archives
```

See `docs/PLATFORMS.md` for platform setup notes.
