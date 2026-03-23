# Dataset Policy

## Behavior source of truth
This repository is a deterministic regression corpus for `blux-ca`. It detects drift in the real engine and must not be treated as the definition of engine behavior.

## Frozen dataset-to-engine mapping
- Dataset line: `cA V1.0 Dataset`
- Active dataset version file: `DATASET_VERSION = cA-1.0-pro`
- Mapped engine line: `blux-ca cA-1.0-pro`
- Mapping record: `DATASET_ENGINE_MAPPING.json`
- Mapping freeze date: `2026-03-22`
- Fixture metadata field carrying the active engine line: `metadata.model_version`
- Archived compatibility line coverage retained under `fixtures/legacy_outputs/archives/`: `cA-0.4` through `cA-1.0`

## Fixture update discipline
Update fixtures only when at least one of the following is true:
1. The live engine output changed and the change is accepted.
2. The stored fixture omitted real stable engine metadata or otherwise misrepresented the contract.
3. A genuine coverage gap exists and filling it improves deterministic representative coverage.

Do not add aspirational behavior, speculative policy outputs, or redundant near-duplicates.

## Required update flow
1. Confirm current engine behavior against the fixture goal.
2. Update affected expectations, schemas, scripts, metadata, and docs in the same pass when the contract changes.
3. Keep policy-pack and profile-specific outputs in explicit directories rather than merging them into ambiguous shared expectations.
4. Preserve old accepted outputs only in `archives/` when compatibility history matters.
5. Run until clean:
   - `python scripts/validate_dataset.py`
   - `python scripts/verify_fixtures.py --engine-root /path/to/blux-ca --policy-pack <pack>`
   - or `python scripts/verify_fixtures.py --actual-root <captured-runs> --policy-pack <pack>`
   - `python scripts/export_jsonl.py --include-archives --write-sha256`
6. Re-run export and confirm byte-identical output.

## Output contract discipline
- `expected_artifact.json` and `expected_verdict.json` are the frozen dataset-side bridge envelopes; live verification must map them truthfully back to the real engine's `artifact.json` / `verdict.json` outputs.
- fixture-local `report.json` files are dataset bridge metadata; the live engine itself emits a single acceptance `report.json`, and verification must compare that real report without inventing unsupported engine files or flags.
- Verification may normalize volatile fields such as timestamps, run IDs, trace IDs, and durations, but it must not simplify or invent stable semantics.
- `status` and `outcome` must remain aligned.
- Archived compatibility outputs must keep their historical `version`/`engine.line` values while still referencing the active dataset version in `engine.dataset_version`.

## Export readiness rules
Every exported row must deterministically map to:
- one `goal.json`
- one expected artifact envelope
- one expected verdict envelope
- optionally one expected report envelope
- one metadata object that includes dataset freeze fields plus policy/profile/archive lineage

The export row order is deterministic by fixture, archive lineage, profile, and policy pack.

## Review expectations
- Keep fixture organization deterministic.
- Keep the dataset-to-engine mapping explicit everywhere.
- Keep docs truthful and current.
- Treat stale wording, obsolete structures, and dead references as bugs.
