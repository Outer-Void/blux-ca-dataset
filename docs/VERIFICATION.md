# Verification

## Purpose
Verification compares this dataset's expected envelopes against either:
1. a live local `blux-ca` engine invocation, or
2. a captured directory of real engine outputs.

This repo detects drift. It does not prescribe behavior independent of the engine.

## Canonical verification commands
Captured real-engine run directory:
```bash
python scripts/verify_fixtures.py --actual-root runs --policy-pack cA-pro
python scripts/verify_fixtures.py --actual-root runs --policy-pack cA-mini
python scripts/verify_fixtures.py --actual-root runs --policy-pack cA-pro --profile cpu
```

Direct live-engine invocation:
```bash
python scripts/verify_fixtures.py \
  --engine-cmd 'python -m blux_ca.run --goal {goal} --out-dir {out_dir} --policy-pack {policy_pack} --profile {profile}' \
  --policy-pack cA-pro
```

## Expected actual output layout
The actual root must contain one directory per fixture with:
- `artifact.json`
- `verdict.json`
- optional `report.json`

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
