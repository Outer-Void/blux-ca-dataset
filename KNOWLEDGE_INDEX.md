# Knowledge Index (BLUX Big-Bang)

## Key Decisions & Invariants
- The capability universe is driven by `universe/registry.json` plus per-capability manifests.
- Every manifest must map to at least one pillar: Unity, Responsibility, Right Action, Risk, Worth.
- Registry + manifest schema drift is blocked by `python tools/universe_validate.py`.
- Router/controller/evaluator loop is centralized in `tools/universe_router.py`.

## Where to Find Things
- Registry: `universe/registry.json`
- Manifests: `universe/manifests/*.json`
- Router/controller/evaluator: `tools/universe_router.py`
- Validator guardrail: `tools/universe_validate.py`
- Universe documentation + demo commands: `UNIVERSE_MAP.md`

## Safe Extension Guide
1. Add a manifest in `universe/manifests/` (include pillars + entrypoint).
2. Register the capability in `universe/registry.json`.
3. If it’s an evaluator, extend `evaluate_job` in `tools/universe_router.py`.
4. Run `python tools/universe_validate.py` before release.
