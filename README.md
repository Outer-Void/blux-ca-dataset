# blux-ca-dataset

Deterministic fixtures and regression cases for `blux-ca`.

## Dataset charter
- Datasets detect drift; they do not define behavior.
- Fixtures are deterministic and versioned for reproducibility.
- Update fixtures only with deliberate version bumps.
- Phase 1 provides schema + minimal fixtures and a tiny verifier.

## Structure (Phase 1)
- `schemas/` — JSON Schemas for goals, expected artifacts, and expected verdicts.
- `fixtures/` — Deterministic fixture bundles.
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
```

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
