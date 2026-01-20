# BLUX-cA Dataset Spine

## What this repository is
A dataset spine for BLUX-cA: schemas, versioned taxonomy and rubrics, evaluation/redteam metadata, and manifests. It is model-agnostic and intended for dataset publication and auditability.

## What this repository is NOT
- **No profiling** or user targeting.
- **No runtime agent**, inference, or execution environment.
- **No enforcement** or policy engine; this repo only defines data and metadata.

## Provenance & Privacy Policy
- **Data minimization:** Only the fields required for dataset items and annotations are retained.
- **Sanitization:** Entries are curated to avoid personal data exposure.
- **No PII by default:** The dataset is designed to exclude personally identifying information.
- **Traceability:** Versioned taxonomy, rubrics, and eval profiles provide auditability without runtime logic.

## Version Mapping (discernment_report schema)
When referencing this dataset from a `discernment_report` schema, use:
- `taxonomy_version`: from `taxonomy/version.json` (`illusion_taxonomy@1.0.0`).
- `rubric_version`: from `rubrics/version.json` (`epistemic_posture@1.0.0`).
- `eval_profile`: from `eval/metadata.json` (`eval-profile-v1`).

## Repository Structure
```
blux-ca-dataset/
├── taxonomy/                 # illusion taxonomy + version file
├── rubrics/                  # epistemic posture rubric + version file
├── eval/                     # evaluation sets + metadata
├── redteam/                  # redteam metadata
├── manifests/                # dataset manifests with checksum placeholders
├── data/                     # dataset JSONL
├── prompts/                  # system prompt placeholders
├── docs/                     # documentation
└── meta/                     # supplemental metadata
```

## Data Format
Each line in every domain file is JSON with a fixed schema containing only a `messages` array:
```json
{"messages": [
  {"role": "system", "content": "<SYSTEM_PROMPT_FROM_BLUX_CA>"},
  {"role": "user", "content": "..."},
  {"role": "assistant", "content": "..."}
]}
```

## Notes
- Evaluation probes live in `eval/` and are kept separate from dataset items in `data/`.
- Versioned taxonomy and rubric files live in `taxonomy/` and `rubrics/` respectively.
