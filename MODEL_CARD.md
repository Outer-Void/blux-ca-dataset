# BLUX-cA Dataset Card

## Dataset Summary
BLUX-cA is a model-agnostic dataset containing prompts, responses, and evaluation probes for constitutional alignment. It reinforces one unified identity: clarity, accountability, refusal of harm/manipulation, and auditable reasoning. No model weights are included.

## Intended Uses
- Supervised fine-tuning and preference alignment for assistants that need clear boundaries and transparent reasoning.
- Evaluation of identity consistency, refusal strength, and reasoning competence.
- Curriculum for red-teaming and safety reviews.

## Out-of-Scope Uses
- Not medical, legal, or financial advice.
- Not for producing deceptive, exploitative, or harmful outputs.
- Not a training pipeline; no fine-tuning scripts are provided.

## Data Structure
- Domain JSONL files (500 examples each) under `data/` with `messages` arrays and a fixed system placeholder `<SYSTEM_PROMPT_FROM_BLUX_CA>`.
- Audit Notes appear on ethically loaded samples, capturing classification, applied reasoning chain, risks, and next steps.
- Evaluation probes in `eval/` are for gating, not training.

## Safety
- Harmful and manipulative user requests are met with refusals and redirection.
- Red-team probes expect refusal-only behavior.
- Audit Notes make high-risk decisions reviewable.

## Licensing
- Default: Apache License 2.0 (`LICENSE`, `NOTICE`).
- Commercial option available for proprietary/closed-source usage (`COMMERCIAL_LICENSE.md`, contact theoutervoid@outlook.com).
- Contributions default to Apache-2.0 unless otherwise agreed.

## Limitations and Known Gaps
- The dataset encodes a specific constitutional stance; models without compatible pretraining may require additional alignment.
- Domain coverage is broad but not exhaustive; always run evaluation probes after modifications.
- No guarantee of legal sufficiency; human review is required for sensitive deployments.
