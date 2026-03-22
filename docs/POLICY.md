# Dataset Policy

## Behavior source of truth
This repository is a deterministic regression corpus for `blux-ca`. It detects drift in the real engine; it does not define engine behavior.

## Version mapping
- `cA V1.0 Dataset` maps to engine line `cA-1.0-pro`.
- `cA-1.0-pro` is the active dataset line.
- Any retained `cA-1.0` and earlier data belongs under `fixtures/*/archives/` for compatibility verification only.

## Fixture governance
Update fixtures only when at least one of these is true:
1. The real engine output changed and the change is accepted.
2. A schema or contract issue made the stored fixture incomplete or misleading.
3. A missing coverage category is necessary to keep the corpus representative and deterministic.

Do not add aspirational outputs, speculative policy behavior, or redundant near-duplicates.

## Required update flow
1. Verify current engine behavior against the fixture goal.
2. Update the affected fixture inputs, expectations, schemas, scripts, and docs in the same pass when the contract changes.
3. Keep policy-pack and profile-specific outputs in their explicit directories rather than merging them into a single ambiguous expectation.
4. Preserve old accepted outputs only in `archives/` when compatibility history matters.
5. Run:
   - `python scripts/validate_dataset.py`
   - `python scripts/verify_fixtures.py --actual-root <runs> --policy-pack <pack>`
6. Re-run checks until clean and deterministic.

## Export readiness rules
Every exportable expectation row must be able to deterministically map to:
- one `goal.json`
- one expected artifact
- one expected verdict
- one metadata object derived from fixture metadata plus explicit path lineage

## Review expectations
- Keep fixture organization deterministic.
- Keep version mapping explicit.
- Keep docs current with the actual corpus.
- Treat stale wording and obsolete references as bugs.
