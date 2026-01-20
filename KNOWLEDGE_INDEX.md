# Knowledge Index (Dataset Spine)

## Key Decisions & Invariants
- Dataset spine only: schemas, taxonomy, rubrics, eval/redteam metadata, and manifests.
- No runtime agent, inference, or execution tooling lives in this repository.
- Versioned taxonomy and rubric files drive dataset references and auditability.

## Where to Find Things
- Taxonomy: `taxonomy/`
- Rubrics: `rubrics/`
- Evaluation metadata: `eval/metadata.json`
- Red team metadata: `redteam/metadata.json`
- Manifests (checksums placeholders): `manifests/`
- Dataset items: `data/*.jsonl`

## Extension Guide (Data Only)
1. Add or update taxonomy/rubrics versions.
2. Add eval/redteam metadata entries.
3. Update manifests with release checksums.
