import hashlib
import json
import os
import re
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_PATH = os.path.join(ROOT, "meta", "manifest.json")


def sha256_file(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest() -> dict:
    with open(MANIFEST_PATH, "r", encoding="utf-8") as handle:
        return json.load(handle)


def scan_training_file(path: str) -> list[str]:
    errors: list[str] = []
    with open(path, "r", encoding="utf-8") as handle:
        content = handle.read()

    prohibited_terms = [
        r"\bALLOW\b",
        r"\bBLOCK\b",
        r"\bREQUIRE_CONFIRM\b",
        r"guard_receipt",
        r"\bexecute\b",
        r"subprocess",
        r"os\.system",
        r"\bshell\b",
        r"\bsudo\b",
        r"\btoken\b",
        r"capability_token",
    ]
    directive_terms = [
        r"\byou should\b",
        r"\bi recommend\b",
        r"\bdo this command\b",
        r"\brun this command\b",
    ]
    pii_terms = [
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?){1}\d{3}[-.\s]?\d{4}\b",
        r"\b(?:street|st\.|avenue|ave\.|road|rd\.|boulevard|blvd\.|lane|ln\.|drive|dr\.|suite|ste\.|apartment|apt\.|unit|po box|p\.o\. box)\b",
    ]

    for pattern in prohibited_terms:
        if re.search(pattern, content, flags=re.IGNORECASE):
            errors.append(f"{path}: prohibited term match: {pattern}")

    for pattern in directive_terms:
        if re.search(pattern, content, flags=re.IGNORECASE):
            errors.append(f"{path}: assistant directive match: {pattern}")

    for pattern in pii_terms:
        if re.search(pattern, content, flags=re.IGNORECASE):
            errors.append(f"{path}: potential PII match: {pattern}")

    return errors


def validate_manifest(manifest: dict) -> list[str]:
    errors: list[str] = []

    all_entries = manifest.get("training_files", []) + manifest.get("eval_files", [])
    for entry in all_entries:
        path = entry.get("path")
        expected = entry.get("sha256")
        if not path or not expected:
            errors.append(f"Manifest entry missing path or sha256: {entry}")
            continue
        abs_path = os.path.join(ROOT, path)
        if not os.path.exists(abs_path):
            errors.append(f"Missing file referenced in manifest: {path}")
            continue
        actual = sha256_file(abs_path)
        if actual != expected:
            errors.append(f"Checksum mismatch for {path}: {actual} != {expected}")

    return errors


def main() -> int:
    if not os.path.exists(MANIFEST_PATH):
        print("Missing manifest: meta/manifest.json")
        return 1

    manifest = load_manifest()
    errors: list[str] = []

    errors.extend(validate_manifest(manifest))

    training_files = [entry["path"] for entry in manifest.get("training_files", [])]
    for path in training_files:
        abs_path = os.path.join(ROOT, path)
        if not os.path.exists(abs_path):
            continue
        errors.extend(scan_training_file(abs_path))

    if errors:
        print("\n".join(errors))
        return 1
    print("Dataset physics checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
