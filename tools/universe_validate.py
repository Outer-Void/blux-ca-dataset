import argparse
import json
from pathlib import Path

ALLOWED_PILLARS = {"Unity", "Responsibility", "Right Action", "Risk", "Worth"}
ALLOWED_TYPES = {"tool", "evaluator"}
REQUIRED_MANIFEST_FIELDS = {
    "id",
    "name",
    "type",
    "description",
    "entrypoint",
    "inputs",
    "outputs",
    "pillars",
    "owner",
    "version",
}


def parse_args():
    parser = argparse.ArgumentParser(description="Validate the BLUX capability registry and manifests")
    parser.add_argument(
        "--registry",
        default="universe/registry.json",
        help="Path to the registry file (default: universe/registry.json)",
    )
    return parser.parse_args()


def load_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def validate_registry(registry_path: Path):
    errors = []
    registry = load_json(registry_path)
    if "version" not in registry:
        errors.append("Registry missing version")
    capabilities = registry.get("capabilities")
    if not isinstance(capabilities, list) or not capabilities:
        errors.append("Registry capabilities must be a non-empty list")
        return errors

    for idx, cap in enumerate(capabilities, 1):
        missing = [field for field in ["id", "name", "type", "manifest", "status"] if field not in cap]
        if missing:
            errors.append(f"Capability {idx} missing fields: {', '.join(missing)}")
            continue
        if cap["type"] not in ALLOWED_TYPES:
            errors.append(f"Capability {cap['id']} has invalid type '{cap['type']}'")
        manifest_path = registry_path.parent / cap["manifest"]
        if not manifest_path.exists():
            errors.append(f"Capability {cap['id']} manifest missing at {manifest_path}")
            continue
        errors.extend(validate_manifest(manifest_path, cap))
    return errors


def validate_manifest(path: Path, capability):
    errors = []
    manifest = load_json(path)
    missing_fields = REQUIRED_MANIFEST_FIELDS - set(manifest.keys())
    if missing_fields:
        errors.append(
            f"Manifest {path} missing fields: {', '.join(sorted(missing_fields))}"
        )
        return errors

    if manifest["id"] != capability["id"]:
        errors.append(
            f"Manifest {path} id '{manifest['id']}' does not match registry id '{capability['id']}'"
        )
    if manifest["type"] != capability["type"]:
        errors.append(
            f"Manifest {path} type '{manifest['type']}' does not match registry type '{capability['type']}'"
        )
    if not isinstance(manifest["inputs"], list):
        errors.append(f"Manifest {path} inputs must be a list")
    if not isinstance(manifest["outputs"], list):
        errors.append(f"Manifest {path} outputs must be a list")
    pillars = manifest.get("pillars", [])
    invalid_pillars = [pillar for pillar in pillars if pillar not in ALLOWED_PILLARS]
    if invalid_pillars:
        errors.append(
            f"Manifest {path} has invalid pillars: {', '.join(sorted(invalid_pillars))}"
        )
    if not pillars:
        errors.append(f"Manifest {path} must include at least one pillar")
    return errors


def main():
    args = parse_args()
    registry_path = Path(args.registry)
    if not registry_path.exists():
        raise SystemExit(f"Registry not found: {registry_path}")

    errors = validate_registry(registry_path)
    if errors:
        print("Registry validation failed:")
        for error in errors:
            print(f" - {error}")
        raise SystemExit(1)

    print("Registry and manifests are valid.")


if __name__ == "__main__":
    main()
