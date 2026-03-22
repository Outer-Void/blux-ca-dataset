# Dataset Policy

## Behavior source of truth
This repository is a deterministic regression corpus for `blux-ca`. It detects drift in the real engine; it does not define engine behavior.

## Dataset-to-engine mapping
- Dataset line: `cA V1.0 Dataset`
- Active dataset version file: `DATASET_VERSION = cA-1.0-pro`
- Mapped live local engine line: `blux-ca cA-1.0-pro`
- Authoritative mapping record: `DATASET_ENGINE_MAPPING.json`
- Fixture metadata field carrying the engine line: `metadata.model_version`

## Fixture governance
Update fixtures only when at least one of these is true:
1. The real engine output changed and the change is accepted.
2. The stored fixture omitted real engine metadata or otherwise represented the contract inaccurately.
3. A missing coverage category is necessary to keep the corpus representative and deterministic.

Do not add aspirational outputs, speculative policy behavior, or redundant near-duplicates.

## Required update flow
1. Verify current engine behavior against the fixture goal.
2. Update the affected fixture inputs, expectations, schemas, scripts, and docs in the same pass when the contract changes.
3. Keep policy-pack and profile-specific outputs in explicit directories rather than merging them into a single ambiguous expectation.
4. Preserve old accepted outputs only in `archives/` when compatibility history matters.
5. Run:
   - `python scripts/validate_dataset.py`
   - `python scripts/verify_fixtures.py --engine-cmd '<local blux-ca command template>' --policy-pack cA-pro`
   - or `python scripts/verify_fixtures.py --actual-root <captured-runs> --policy-pack <pack>` when comparing a pre-recorded real engine run
6. Re-run checks until clean and deterministic.

## Output contract discipline
- `expected_artifact.json`, `expected_verdict.json`, and `report.json` must keep the engine envelope fields that the live engine emits for deterministic regression: `version`, `contract_version`, `fixture_id`, `engine`, and `request`.
- The dataset may normalize away volatile fields such as timestamps, run IDs, and durations during verification, but it must not invent or simplify stable engine semantics.
- `status` and `outcome` must remain aligned.

## Export readiness rules
Every exportable expectation row must be able to deterministically map to:
- one `goal.json`
- one expected artifact
- one expected verdict
- optionally one expected report
- one metadata object derived from fixture metadata plus explicit path lineage

## Review expectations
- Keep fixture organization deterministic.
- Keep version mapping explicit.
- Keep docs current with the actual corpus.
- Treat stale wording, obsolete structures, and dead references as bugs.
