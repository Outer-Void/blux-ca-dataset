# BLUX-cA Dataset

Unified dataset, prompts, and evaluation probes for the BLUX-cA constitutional spine. This repository is model-agnostic and ships a ready-to-publish dataset (no training pipeline) with validation tooling, release gating, and dual licensing.

## Overview
- **Identity lock:** BLUX-cA stays clear, accountable, audit-friendly, and refuses manipulation or harm.
- **Discernment compass:** Struggler vs Indulger/Justifier vs Unclear, with refusals for harmful or manipulative requests.
- **Auditability:** Safety/ethics-loaded responses include structured Audit Notes for transparent review.
- **Deterministic assets:** JSONL files use a fixed system placeholder (`<SYSTEM_PROMPT_FROM_BLUX_CA>`) so prompts remain separable from data.

## Repository Structure
```
blux-ca-dataset/
├── AUDIT_LOG.md
├── COMMERCIAL_LICENSE.md       # Commercial licensing template (Outer Void)
├── KNOWLEDGE_INDEX.md
├── LICENSE                     # Apache-2.0
├── NOTICE                      # Attribution placeholder
├── README.md
├── MODEL_CARD.md               # Dataset card for Hugging Face
├── UNIVERSE_MAP.md
├── prompts/
│   ├── system_core.txt
│   ├── system_coding.txt
│   └── system_governance.txt
├── data/
│   ├── core.jsonl
│   ├── coding.jsonl
│   ├── governance.jsonl
│   ├── safety.jsonl
│   ├── reasoning.jsonl
│   ├── creation.jsonl
│   ├── conversation.jsonl
│   ├── efficiency.jsonl
│   └── relationships.jsonl
├── eval/
│   ├── identity_probes.jsonl
│   ├── red_team.jsonl
│   └── capability_probes.jsonl
├── rubric/
│   └── labeling_rubric.md
├── tools/
    ├── generate_dataset.py
    ├── sample_review.py
    ├── summarize_dataset.py
    ├── universe_router.py
    ├── universe_validate.py
    └── validate_jsonl.py
└── universe/
    └── manifests/
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
- **System prompt:** Always the placeholder string above (apply domain overlays separately).
- **Message roles:** `system`, `user`, `assistant`.
- **Audit Notes:** When safety/ethics are present, assistant content ends with:
  ```
  ## Audit Notes
  - classification: Struggler | Indulger | Unclear
  - applied: Law | Strategy | Tactic (or chain)
  - risks:
    - ...
  - next_step:
    - ...
  ```

## JSONL Counts
| File | Lines |
| --- | ---: |
| data/coding.jsonl | 500 |
| data/conversation.jsonl | 500 |
| data/core.jsonl | 500 |
| data/creation.jsonl | 501 |
| data/efficiency.jsonl | 500 |
| data/governance.jsonl | 500 |
| data/reasoning.jsonl | 500 |
| data/relationships.jsonl | 500 |
| data/safety.jsonl | 500 |
| eval/capability_probes.jsonl | 10 |
| eval/identity_probes.jsonl | 10 |
| eval/red_team.jsonl | 10 |

## Domains
- **core:** identity, ethics, boundary-setting, manipulation detection.
- **safety:** refusals, redirection, safety framing (no harmful instructions).
- **governance:** power, institutions, accountability; never outsource morality to algorithms.
- **coding:** debugging discipline, secure patterns, refusing exploit requests.
- **reasoning:** structured thinking, assumption checks, tradeoffs.
- **creation:** proposals, plans, documents, structured outputs without fluff.
- **conversation:** concise, grounded dialogue; no emotional roleplay.
- **efficiency:** compression, bullet summaries, minimal questions, clarity.
- **relationships:** boundaries, conflict de-escalation, accountability, anti-manipulation.

## Evaluation Harness (never for training)
- `eval/identity_probes.jsonl`: stress-tests the BLUX-cA spine, audit rules, and refusal stance.
- `eval/red_team.jsonl`: adversarial prompts expecting firm refusals and boundary clarity.
- `eval/capability_probes.jsonl`: reasoning, coding, and clarity checks that must remain aligned.

Evaluation probes live in `eval/` and are kept separate from training data in `data/`.

**Publish gate:** Do not release a new dataset version unless all probes are satisfied. Failures include soft compliance, emotional roleplay, eroded refusals, or loss of auditability.

## Tooling
All tools are CPU-only and deterministic.

### Validate JSONL
```
python tools/validate_jsonl.py            # defaults to data/*.jsonl
python tools/validate_jsonl.py data/core.jsonl
```
Checks: JSON parse, schema/roles, system placeholder, non-empty user/assistant, Audit Notes shape, and expected line counts per domain file.

### Summarize dataset
```
python tools/summarize_dataset.py         # per-file counts, classifications, Audit Notes, top prompts
python tools/summarize_dataset.py data/core.jsonl --top 10
```

### Sample for review
```
python tools/sample_review.py             # deterministic samples -> review/sample_<date>.md
python tools/sample_review.py data/core.jsonl --n 5 --seed 7
```

### Regenerate deterministically (optional)
```
python tools/generate_dataset.py          # re-creates all domain files with the fixed seed
```

## Versioning Strategy
- **v0.1:** lock the core identity pack.
- **v0.2:** add capability packs (reasoning, coding, governance, relationships).
- **v0.3:** add efficiency/compression refinements.
Every increment must pass validation and evaluation probes before release.

## Release Checklist
- [ ] `python tools/validate_jsonl.py` passes for all domain files (see JSONL counts above).
- [ ] Evaluation probes reviewed/updated; failures addressed before publish.
- [ ] `python tools/sample_review.py` run and reviewed; flagged lines pruned/regenerated.
- [ ] Licensing confirmed (Apache-2.0 by default; commercial option via Outer Void).
- [ ] Hugging Face dataset card (`MODEL_CARD.md`) updated and pushed/tagged.

## Licensing
- Default license: **Apache License 2.0** (see `LICENSE` and `NOTICE`).
- **Commercial license** available for proprietary/closed-source usage via Outer Void (`COMMERCIAL_LICENSE.md`, contact: theoutervoid@outlook.com).
- Contributions are accepted under Apache-2.0 unless otherwise agreed in writing. This repository does not provide legal advice.

## Hugging Face Publishing
1. Validate and sample-review the dataset.
2. Copy `MODEL_CARD.md` to the HF dataset repo README.
3. Upload `data/`, `eval/`, `prompts/`, `rubric/`, and tooling scripts.
4. Tag the release (e.g., `v0.2`) and document probe status in the card.
