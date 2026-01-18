# Repository Scan Report (Pass 1)

## Tree Summary

Top-level listing:

```
AUDIT_LOG.md
COMMERCIAL_LICENSE.md
KNOWLEDGE_INDEX.md
LICENSE
MODEL_CARD.md
NOTICE
README.md
UNIVERSE_MAP.md
data/
eval/
prompts/
rubric/
tools/
universe/
```

Concise tree (depth 2–3):

```
.
├── data
├── eval
├── prompts
├── rubric
├── tools
└── universe
    └── manifests
```

## JSONL Line Counts

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

## JSONL Parse Errors (first 50 lines per file)

No parse errors detected in the first 50 lines of any JSONL file.

## Schema Sample (first object per data/*.jsonl)

- data/coding.jsonl
  - keys: `messages`
  - message roles: `assistant`, `system`, `user`
- data/conversation.jsonl
  - keys: `messages`
  - message roles: `assistant`, `system`, `user`
- data/core.jsonl
  - keys: `messages`
  - message roles: `assistant`, `system`, `user`
- data/creation.jsonl
  - keys: `messages`
  - message roles: `assistant`, `system`, `user`
- data/efficiency.jsonl
  - keys: `messages`
  - message roles: `assistant`, `system`, `user`
- data/governance.jsonl
  - keys: `messages`
  - message roles: `assistant`, `system`, `user`
- data/reasoning.jsonl
  - keys: `messages`
  - message roles: `assistant`, `system`, `user`
- data/relationships.jsonl
  - keys: `messages`
  - message roles: `assistant`, `system`, `user`
- data/safety.jsonl
  - keys: `messages`
  - message roles: `assistant`, `system`, `user`
