# blux-ca-dataset

Deterministic fixtures and regression cases for `blux-ca`.

## Dataset charter
- Datasets detect drift; they do not define behavior.
- Fixtures are deterministic and versioned for reproducibility.
- Update fixtures only with deliberate version bumps.
- Phase 1 provides schema + minimal fixtures and a tiny verifier.

## Structure (Phases 1-4)
- `schemas/` — JSON Schemas for goals, expected artifacts, and expected verdicts.
- `fixtures/` — Deterministic fixture bundles (Phase 1-4).
- `scripts/verify_fixtures.py` — Compares canonical JSON bytes to expected outputs.
- `docs/` — Contributor notes and platform setup.

## Fixture layout
```
fixtures/
  hello/
    goal.json
    expected_artifact.json
    expected_verdict.json
  infeasible/
    goal.json
    expected_artifact.json
    expected_verdict.json
  drift_probe/
    goal.json
    expected_artifact.json
    expected_verdict.json
  multi_file_artifact/
    goal.json
    expected_artifact.json
    expected_verdict.json
    report.json
  patch_bundle/
    goal.json
    expected_artifact.json
    expected_verdict.json
    report.json
  path_traversal/
    goal.json
    expected_artifact.json
    expected_verdict.json
    report.json
  duplicate_paths/
    goal.json
    expected_artifact.json
    expected_verdict.json
    report.json
  unsorted_output/
    goal.json
    expected_artifact.json
    expected_verdict.json
    report.json
```

## Phase 3 fixtures (structural bundles)
- `multi_file_artifact` — Multi-file artifact with canonical ordering.
- `patch_bundle` — Patch bundle with ordered, unified diffs.
- `path_traversal` — Failure case for disallowed `../` paths.
- `duplicate_paths` — Failure case for repeated file paths.
- `unsorted_output` — Failure case for unsorted file listings.

## Phase 4 acceptance harness
Acceptance mode reads `report.json` alongside expected artifacts/verdicts to capture
the harness verdict for structural checks. When running in acceptance mode, emit a
`report.json` per fixture under your run root (e.g., `runs/multi_file_artifact/report.json`)
and compare it to the fixture's `report.json` if present. Fixtures without a
`report.json` can continue to rely on `artifact.json` and `verdict.json` comparisons.

## Verifying outputs
1) Run cA for each `goal.json` and store the outputs under a directory, one folder per
   fixture:
   ```
   runs/
     hello/
       artifact.json
       verdict.json
     infeasible/
       artifact.json
       verdict.json
     drift_probe/
       artifact.json
       verdict.json
   ```
2) Compare canonical JSON bytes against expectations:
   ```bash
   ./scripts/verify_fixtures.py --actual-root runs
   ```

See `docs/PLATFORMS.md` for platform setup notes.
