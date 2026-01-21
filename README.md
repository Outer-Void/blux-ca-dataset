# BLUX-cA Dataset Spine

## What this repository is
A dataset spine for BLUX-cA: discernment-report training samples, eval probes, taxonomy/rubric versions, and manifests. It is model-agnostic and intended for dataset publication and auditability.

This dataset trains **discernment_report** shape + posture scoring + illusion taxonomy references. Outputs are **contract-shaped artifacts** (discernment_report fields), not assistant prose.

## What this repository is NOT
- **No profiling** or user targeting.
- **No runtime agent**, inference, or execution environment.
- **No enforcement**, receipt issuance, or policy engine; this repo only defines data and metadata.
- **No prescriptive advice or execution suggestions**; outputs are discernment reports only.
- **No orchestration** or authority posture; no "allow/deny/block" decisions live here.

## Provenance & Privacy Policy
- **Data minimization:** Only the fields required for dataset items and annotations are retained.
- **Sanitization:** Entries are curated to avoid personal data exposure.
- **No PII by default:** The dataset is designed to exclude personally identifying information.
- **No raw logs:** Only curated user text snippets or summaries are allowed.
- **Traceability:** Versioned taxonomy, rubrics, and eval profiles provide auditability without runtime logic.

## Discernment Report Framing
- Outputs are **DISCERNMENT_REPORT** artifacts (posture, signals, uncertainty, handoff).
- The dataset **never** includes policy enforcement or operational instructions.
- Separation of concerns:
  - **Guard** enforces.
  - **Lite** executes.
  - **Quantum** routes.
  - **Reg** handles trust.

## Version Mapping (discernment_report schema)
When referencing this dataset from a `discernment_report` schema, use:
- `taxonomy_version`: from `taxonomy/version.json` (`illusion_taxonomy@1.0.0`).
- `rubric_version`: from `rubrics/version.json` (`epistemic_posture@1.0.0`).
- `eval_profile`: from `eval/metadata.json` (`eval-profile-v1`).

## Repository Structure
```
blux-ca-dataset/
├── data/                     # training-ready discernment report samples
├── eval/                     # eval probes + legacy quarantine (not for training)
├── meta/                     # canonical manifest, checksums
├── docs/                     # dataset spec + governance
├── taxonomy/                 # illusion taxonomy + version file
├── rubrics/                  # epistemic posture rubric + version file
├── redteam/                  # redteam metadata
├── manifests/                # legacy manifests (non-canonical)
└── prompts/                  # system prompt placeholders
```

### Separation of concerns
- `data/` contains **training samples only** (discernment_report outputs).
- `eval/` contains **red-team probes and evaluation sets**, including legacy quarantine data.
- Training content must **never** include enforcement, receipt issuance, execution, or orchestration language.

## Data Format
Each training sample is JSONL with:
- `input.user_text` (optional `client_provided_memory` references only).
- `output.discernment_report` shaped to `blux://contracts/discernment_report.schema.json`.
- `dataset_refs` (taxonomy/rubric versions, optional eval profile).
- `notes` (non-sensitive labeling notes).

See `docs/DATASET_SPEC.md` for the canonical sample spec.

## Notes
- Evaluation probes live in `eval/` and are kept separate from dataset items in `data/`.
- Versioned taxonomy and rubric files live in `taxonomy/` and `rubrics/` respectively.
- The canonical manifest is `meta/manifest.json`.
