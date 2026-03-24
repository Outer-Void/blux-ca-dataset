---
pretty_name: BLUX cA Dataset
license: other
license_name: BLUX Proprietary License
tags:
  - deterministic-ai
  - code-generation
  - validation
  - reasoning
task_categories:
  - text-generation
---

# blux-ca-dataset

Deterministic fixtures, regression cases, and export material for `blux-ca`.

## Dataset card summary (HuggingFace-ready)
- **Dataset structure:** fixture-derived JSONL rows with deterministic canonical serialization.
- **Row format:** each row includes `input`, `artifact`, `verdict`, optional `report`, `source_paths`, and `metadata`.
- **Generation method:** rows are generated from committed fixtures and expected engine envelopes via `scripts/export_jsonl.py`.
- **Determinism guarantee:** export ordering and JSON encoding are fixed; repeated exports on unchanged content are byte-identical.

## Dataset charter
- This repo detects drift in the real `blux-ca` engine; it does **not** define engine behavior.
- The active frozen dataset line is `cA V1.0 Dataset`.
- Canonical mapping lock: **`blux-ca-dataset v1.0 -> cA-1.0-pro`**.
- The authoritative version freeze record is `DATASET_ENGINE_MAPPING.json`.
- `cA-1.0` and earlier lines remain archived only for compatibility checks in `fixtures/*/archives/`.
- Fixture updates are allowed only when the live engine changes, or when stored expectations are missing real stable engine contract fields.
- Current active dataset version: `cA-1.0-pro` from `DATASET_VERSION`.

## Structure
- `schemas/` — JSON Schemas for fixture goals, engine-aligned expected artifacts/verdicts/reports, and export rows.
- `fixtures/` — deterministic fixture bundles aligned to the `cA-1.0-pro` engine line.
- `scripts/validate_dataset.py` — validates fixture layout, metadata completeness, version mapping, and export derivation.
- `scripts/verify_fixtures.py` — verifies expected outputs against a captured dataset-format run directory or against a real local `blux-ca` checkout using the supported `accept` CLI.
- `scripts/export_jsonl.py` — emits the single canonical deterministic JSONL export for freeze and HuggingFace handoff.
- `exports/` — generated deterministic JSONL artifacts and checksums.
- `docs/` — policy, platform, verification, and export notes.

## Dataset-to-engine version freeze
| Dataset field | Frozen value |
| --- | --- |
| Dataset ID | `cA V1.0 Dataset` |
| Dataset repo | `blux-ca-dataset` |
| Dataset semver | `v1.0` |
| Dataset version | `cA-1.0-pro` |
| Engine name | `blux-ca` |
| Engine line | `cA-1.0-pro` |
| Mapping | `blux-ca-dataset v1.0 -> cA-1.0-pro` |
| Fixture contract | `fixture-contract-1.1` |
| Output contract | `blux-ca-output-1.1` |
| Report contract | `blux-ca-report-1.1` |
| Export contract | `blux-ca-export-row-1.2` |
| Mapping date | `2026-03-22` |

## JSONL structure lock
Each exported row must include:
- `input`
- `artifact`
- `verdict`
- `metadata` with:
  - `model_version`
  - `contract_version`
  - `policy_pack_id`
  - `profile_id`

## Canonical validation, verification, and export flow
```bash
python scripts/validate_dataset.py
python scripts/verify_fixtures.py --engine-root /absolute/path/to/blux-ca --policy-pack cA-pro
python scripts/export_jsonl.py --include-archives --write-sha256
```

If a direct local engine checkout is unavailable, fallback to an already-captured dataset-format run root:
```bash
python scripts/verify_fixtures.py --actual-root <captured-dataset-format-runs> --policy-pack cA-pro
```

`verify_fixtures.py` generates engine-compatible temporary fixture goals and invokes the real supported CLI:
`python -m blux_ca accept --fixtures <generated-bridge-dir> --out <temp-run-dir> [--profile <id>]`.
It does **not** assume unsupported engine flags such as `--policy-pack` or `--out-dir`.
When `--profile` is omitted, acceptance-report `profile_id` is treated as valid when absent or `"default"` (matching live engine behavior).

## Canonical export lock
The one canonical export path is:
- `exports/blux-ca-dataset.jsonl`

Running export twice on unchanged repo content must yield an identical SHA-256 hash.

## License
Repository license is proprietary (`LICENSE`); publishing/upload must preserve the same licensing constraints.
