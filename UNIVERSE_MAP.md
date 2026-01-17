# BLUX Universe Map

## Modules & Interfaces
- **universe/registry.json**: canonical capability index (id, type, manifest path).
- **universe/manifests/*.json**: per-capability manifests (entrypoint, IO schema, pillars).
- **tools/universe_router.py**: router/controller/evaluator loop for capability routing.
- **tools/universe_validate.py**: schema validator guardrail for registry + manifests.

## Capability Surface Area
| Capability | Type | Interface | Purpose |
| --- | --- | --- | --- |
| dataset.validate | tool | `python tools/validate_jsonl.py [paths...]` | Enforce JSONL schema + audit notes. |
| dataset.summarize | tool | `python tools/summarize_dataset.py [paths...]` | Report counts + audit note stats. |
| dataset.sample_review | tool | `python tools/sample_review.py [path] --n N --seed S` | Deterministic samples for review. |
| eval.identity_probe | evaluator | `python tools/universe_router.py --capability eval.identity_probe` | Route identity probes for evaluation checks. |

## Demo Commands (End-to-End Proof)
```bash
python tools/universe_validate.py
python tools/universe_router.py --capability dataset.validate
python tools/universe_router.py --capability eval.identity_probe --payload '{"probe_path": "eval/identity_probes.jsonl"}'
```

## Extension Hooks
- Add new capabilities by creating a manifest in `universe/manifests/` and registering it in `universe/registry.json`.
- Add evaluators by extending `evaluate_job` in `tools/universe_router.py`.
- Keep schema drift in check by running `python tools/universe_validate.py` in CI.
