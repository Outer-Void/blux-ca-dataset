# Verification

## Purpose
Verification compares this dataset's expected bundles against either:
1. a real local `blux-ca` checkout invoked through its supported `accept` CLI, or
2. a captured directory of dataset-format outputs that already match this repo's bridge contract.

This repo detects drift. It does not prescribe behavior independent of the engine.

## Canonical verification command/path freeze
Real local `blux-ca` checkout (canonical):
```bash
python scripts/verify_fixtures.py --engine-root /absolute/path/to/blux-ca --policy-pack cA-pro
```

The verifier internally generates engine-compatible temporary fixture goals and runs:
`python -m blux_ca accept --fixtures <generated-bridge-dir> --out <temp-run-dir> [--profile <id>]`.
Unsupported engine flags are intentionally omitted; the real engine currently exposes `--out`, not `--out-dir`, and policy pack selection remains part of the goal payload rather than a CLI flag.

Optional matrix extensions:
```bash
python scripts/verify_fixtures.py --engine-root /absolute/path/to/blux-ca --policy-pack cA-mini
python scripts/verify_fixtures.py --engine-root /absolute/path/to/blux-ca --policy-pack cA-pro --profile cpu
```

Captured dataset-format run directory fallback (only when local engine checkout is unavailable):
```bash
python scripts/verify_fixtures.py --actual-root runs --policy-pack cA-pro
```

## Expected actual output layout
The actual root must contain one directory per fixture with:
- `artifact.json`
- `verdict.json`
- optional `report.json`
- when verifying with `--engine-root`, the live engine writes a single top-level `report.json`; the verifier reads that report plus per-fixture `artifact.json` / `verdict.json` outputs
- profile metadata handling is strict but engine-compatible: with explicit `--profile <id>`, report/profile fields must match `<id>`; without `--profile`, acceptance report `profile_id` may be omitted or `"default"`

For archive comparisons, use:
```text
<actual-root>/archives/<version>/<policy_pack>/<fixture>/artifact.json
<actual-root>/archives/<version>/<policy_pack>/<fixture>/verdict.json
```

## Comparison behavior
- Volatile fields are normalized away: timestamps, run IDs, trace IDs, and durations.
- Stable engine envelope fields are compared deterministically.
- Expected payloads may be a subset only when the engine emits extra non-semantic fields beyond the stored envelope.
- If the local engine is unavailable, verification cannot truthfully be claimed as a live-engine pass; use a captured real-engine run instead.
