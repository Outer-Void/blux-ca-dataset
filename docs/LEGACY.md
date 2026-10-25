# Legacy: the frozen cA 1.0 drift fixtures

`legacy/` holds dataset v1.0 (`cA V1.0 Dataset`), the drift-detection fixtures for the frozen cA 1.0
contract (`blux-ca accept`, `cA-1.0-pro`). It moved there unchanged in Stage 08, together with its
`DATASET_VERSION`, `DATASET_ENGINE_MAPPING.json`, schemas, scripts, docs and canonical export. The scripts
use paths relative to the current directory, so run them from `legacy/`:

```bash
cd legacy
python scripts/validate_dataset.py
python scripts/verify_fixtures.py --engine-root /path/to/blux-ca --policy-pack cA-pro
python scripts/export_jsonl.py --include-archives --write-sha256      # byte-identical exports/
```

CI runs the validation and the `cA-pro`, `cA-mini` and `cpu`-profile verifications on every push.
blux-ca's own CI runs them against a pinned commit of this repository.

## Stage 08 audit of v1.0

| finding | status |
|---|---|
| **The card called it `text-generation`.** cA 1.0's outputs are deterministic template results. | v2's card claims no such task. |
| **The `cA-full` verification fails.** On `policy_pack_matrix` it expects `cA-pro`, and fails identically on every engine commit checked (Stage 07): the expectation itself is wrong. | v1.0 is frozen; CI verifies `cA-pro`, `cA-mini` and `cpu` only. |
| **It covers only the 1.0 contract.** That contract never applies a patch, so there is nothing about changesets, rollback, repair or validation. | v2 covers cA 2 and DAT-validated repair. |
| **There were no splits, per-row licence and provenance, dedup, contamination checks or CI.** | v2 has all of them (docs/ENGINEERING.md). |

The original v1.0 policy, export and platform notes are in `legacy/POLICY.md` and `legacy/docs/`.
