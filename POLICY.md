# Fixture Policy

## Purpose
This dataset detects drift; it does not define behavior. Every fixture is deterministic and
versioned for reproducibility.

## Versioning
- The dataset version is stored in `DATASET_VERSION`.
- Any change to fixtures or expectations **must** include a dataset version bump and
  updated expected outputs for that version.

## Fixture update workflow
1. Bump `DATASET_VERSION` (e.g., `cA-1.0` → `cA-1.1`).
2. Regenerate fixture outputs under the new version directory:
   `fixtures/<case>/expected/<new_version>/<policy_pack_id>/`.
3. Update or add `report.json` when acceptance checks change.
4. Run `./scripts/validate_dataset.py` to confirm layout/version consistency.
5. Run `./scripts/verify_fixtures.py --actual-root <runs> --policy-pack <pack>` against
   newly generated outputs.

## CI gating
CI must fail on drift by running:
- `./scripts/validate_dataset.py`
- `./scripts/verify_fixtures.py --actual-root <runs> --policy-pack <pack>`

Archive compatibility checks (optional but recommended):
- `./scripts/verify_fixtures.py --actual-root <runs> --policy-pack <pack> --include-archives`

## Approvals
- Fixture changes require peer review.
- Any updates to `archives/` must be accompanied by a note explaining why compatibility
  expectations changed.
