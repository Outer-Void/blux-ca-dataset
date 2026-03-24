# Export

## Purpose
`scripts/export_jsonl.py` emits a deterministic JSONL export suitable for:
- GitHub finalization artifacts
- HuggingFace dataset publication
- later training-data generation

## Row contents
Each row contains:
- `source_paths`: repo-relative traceability back to the source fixture files
- `input`: full fixture goal payload
- `artifact`: full expected artifact envelope
- `verdict`: full expected verdict envelope
- `report`: expected report envelope or `null`
- `metadata`: dataset freeze fields plus policy/profile/archive lineage

## Determinism guarantees
- Rows are sorted by fixture ID, archive lineage, profile ID, and policy pack ID.
- JSON serialization is canonicalized with stable key ordering and compact separators.
- Re-running the exporter on the same repo state must produce byte-identical output.
- Optional SHA-256 sidecar files can be written for freeze/handoff verification.

## Canonical command
```bash
python scripts/export_jsonl.py --include-archives --write-sha256
```

This writes the canonical path:
- `exports/blux-ca-dataset.jsonl`
- `exports/blux-ca-dataset.jsonl.sha256`

Version mapping lock carried in metadata:
- `blux-ca-dataset v1.0 -> cA-1.0-pro`

## Export assumptions
- The active dataset freeze maps to `blux-ca cA-1.0-pro`.
- Archived compatibility rows represent accepted historical outputs and are labeled with `metadata.archive_version` and `metadata.source_kind = archive`.
- The export is derived from the dataset; it does not override live engine truth.
