# BLUX-cA Discernment Report Dataset Spec

## Purpose
This dataset trains **discernment report generation** only. Outputs must be contract-shaped artifacts that describe posture, signals, uncertainty, and handoff considerations. The dataset is **not** for assistant advice, execution, or enforcement.

## Boundaries
- **No prescriptive advice** (no instructions or recommendations).
- **No execution or tool invocation** (no commands or automation).
- **No enforcement language** (Guard enforces elsewhere).
- **No raw user logs or PII**; only minimal, curated user text.

## Sample Format (JSONL)
Each line is a JSON object with the following shape:

```json
{
  "input": {
    "user_text": "<minimal user text>",
    "client_provided_memory": ["optional_ref_1", "optional_ref_2"]
  },
  "output": {
    "discernment_report": {
      "schema_ref": "blux://contracts/discernment_report.schema.json",
      "posture": "<posture label>",
      "signals": [
        {"type": "<signal_type>", "evidence": "<summary evidence>"}
      ],
      "uncertainty": {
        "level": "<low|medium|high>",
        "drivers": ["<driver>"]
      },
      "handoff": {
        "needed": true,
        "reason": "<handoff rationale>"
      },
      "boundaries": [
        "no prescriptive advice",
        "no enforcement actions",
        "no execution guidance"
      ]
    }
  },
  "dataset_refs": {
    "taxonomy_version": "illusion_taxonomy@1.0.0",
    "rubric_version": "epistemic_posture@1.0.0",
    "eval_profile": "eval-profile-v1"
  },
  "notes": "<non-sensitive labeling notes>"
}
```

## Provenance Rules
- Do not include raw logs, chat transcripts, or identifiable personal data.
- Use only minimal snippets required to contextualize discernment signals.
- Keep `dataset_refs` aligned with the versions in `taxonomy/version.json` and `rubrics/version.json`.
