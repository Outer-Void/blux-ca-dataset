import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


@dataclass(frozen=True)
class Capability:
    id: str
    name: str
    type: str
    manifest_path: Path
    status: str


@dataclass(frozen=True)
class Manifest:
    id: str
    name: str
    type: str
    description: str
    entrypoint: str
    inputs: List[Dict[str, Any]]
    outputs: List[Dict[str, Any]]
    pillars: List[str]
    owner: str
    version: str
    tags: List[str]


@dataclass(frozen=True)
class Job:
    capability: Capability
    manifest: Manifest
    payload: Dict[str, Any]


def parse_args():
    parser = argparse.ArgumentParser(description="Route requests through the BLUX capability universe")
    parser.add_argument("--registry", default="universe/registry.json", help="Path to registry JSON")
    parser.add_argument("--capability", required=True, help="Capability id to route")
    parser.add_argument(
        "--payload",
        default="{}",
        help="JSON payload to pass to the capability (default: {})",
    )
    return parser.parse_args()


def load_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_registry(path: Path) -> List[Capability]:
    registry = load_json(path)
    capabilities = []
    for entry in registry.get("capabilities", []):
        capabilities.append(
            Capability(
                id=entry["id"],
                name=entry["name"],
                type=entry["type"],
                manifest_path=path.parent / entry["manifest"],
                status=entry["status"],
            )
        )
    return capabilities


def load_manifest(path: Path) -> Manifest:
    data = load_json(path)
    return Manifest(
        id=data["id"],
        name=data["name"],
        type=data["type"],
        description=data["description"],
        entrypoint=data["entrypoint"],
        inputs=data["inputs"],
        outputs=data["outputs"],
        pillars=data["pillars"],
        owner=data["owner"],
        version=data["version"],
        tags=data.get("tags", []),
    )


def route_request(capabilities: List[Capability], capability_id: str) -> Capability:
    for capability in capabilities:
        if capability.id == capability_id:
            return capability
    raise ValueError(f"Capability '{capability_id}' not found")


def build_job(capability: Capability, manifest: Manifest, payload: Dict[str, Any]) -> Job:
    return Job(capability=capability, manifest=manifest, payload=payload)


def evaluate_job(job: Job) -> Dict[str, Any]:
    if job.capability.type == "evaluator" and job.capability.id == "eval.identity_probe":
        probe_path = Path(job.payload.get("probe_path", "eval/identity_probes.jsonl"))
        if not probe_path.exists():
            return {
                "status": "failed",
                "reason": f"Probe file not found: {probe_path}",
            }
        line_count = sum(1 for _ in probe_path.open(encoding="utf-8"))
        return {
            "status": "ok",
            "probe": str(probe_path),
            "lines": line_count,
            "note": "Probe routing verified (file counted).",
        }

    return {
        "status": "ok",
        "capability": job.capability.id,
        "entrypoint": job.manifest.entrypoint,
        "note": "Capability routed (execution not invoked).",
    }


def run_loop(registry_path: Path, capability_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    capabilities = load_registry(registry_path)
    capability = route_request(capabilities, capability_id)
    manifest = load_manifest(capability.manifest_path)
    job = build_job(capability, manifest, payload)
    return evaluate_job(job)


def main():
    args = parse_args()
    registry_path = Path(args.registry)
    payload = json.loads(args.payload)
    result = run_loop(registry_path, args.capability, payload)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
