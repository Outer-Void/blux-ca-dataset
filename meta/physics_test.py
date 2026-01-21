import hashlib
import json
import os
import re
import sys
from typing import Iterable


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


def load_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as handle:
        return handle.read()


def iter_text_files(paths: Iterable[str]) -> Iterable[str]:
    for path in paths:
        if os.path.isdir(path):
            for root, _, files in os.walk(path):
                if root.startswith(os.path.join(ROOT, ".git")):
                    continue
                for filename in files:
                    full_path = os.path.join(root, filename)
                    yield full_path
        else:
            yield path


def extract_assistant_text(sample: dict) -> str:
    if "output" in sample:
        return json.dumps(sample.get("output"), ensure_ascii=False)
    if "messages" in sample:
        parts = []
        for message in sample.get("messages", []):
            if message.get("role") == "assistant":
                parts.append(message.get("content", ""))
        return "\n".join(parts)
    return json.dumps(sample, ensure_ascii=False)


def scan_sample_file(path: str, enforcement_terms: list[str]) -> list[str]:
    errors: list[str] = []
    with open(path, "r", encoding="utf-8") as handle:
        for idx, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                sample = json.loads(line)
                content = extract_assistant_text(sample)
            except json.JSONDecodeError:
                content = line
            for pattern in enforcement_terms:
                if re.search(pattern, content, flags=re.IGNORECASE):
                    errors.append(f"{path}:{idx}: enforcement language match: {pattern}")
    return errors


def scan_pii(paths: Iterable[str], pii_terms: list[str]) -> list[str]:
    errors: list[str] = []
    skip_ext = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".tar", ".gz"}
    for path in iter_text_files(paths):
        if os.path.basename(path).startswith("."):
            continue
        if any(part in path for part in (os.sep + ".git" + os.sep,)):
            continue
        if any(token in path.lower() for token in ("fixtures", "synthetic")):
            continue
        if os.path.splitext(path)[1].lower() in skip_ext:
            continue
        content = load_text(path)
        for pattern in pii_terms:
            if re.search(pattern, content, flags=re.IGNORECASE):
                errors.append(f"{path}: potential PII match: {pattern}")
                break
    return errors


def scan_banned_filenames(paths: Iterable[str]) -> list[str]:
    errors: list[str] = []
    banned_names = {
        "chatlog",
        "chat_log",
        "transcript",
        "dm",
        "dms",
        "message_log",
        "messages",
        "conversation_log",
        "chat_history",
    }
    for path in iter_text_files(paths):
        if os.path.basename(path).startswith("."):
            continue
        name = os.path.splitext(os.path.basename(path))[0].lower()
        if name in banned_names:
            errors.append(f"{path}: banned raw-log filename detected")
    return errors


def scan_schema_drift() -> list[str]:
    errors: list[str] = []
    schema_paths: list[str] = []
    for root, _, files in os.walk(ROOT):
        if root.startswith(os.path.join(ROOT, ".git")):
            continue
        for filename in files:
            if filename.endswith(".schema.json"):
                schema_paths.append(os.path.join(root, filename))
    if schema_paths:
        for path in schema_paths:
            if "non_canonical" not in path:
                errors.append(f"{path}: schema file must be quarantined under non_canonical fixtures")
        if len(schema_paths) > 1:
            errors.append(f"Multiple schema files detected: {schema_paths}")
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
    eval_files = [entry["path"] for entry in manifest.get("eval_files", [])]
    sample_files = [*training_files, *eval_files]

    enforcement_terms = [
        r"\bI will allow\b",
        r"\bI will block\b",
        r"\bI will deny\b",
        r"\bI am enforcing\b",
        r"\benforce policy\b",
        r"\bissue (a )?receipt\b",
        r"\bguard receipt\b",
        r"\bguard_receipt\b",
        r"\bfiling a guard receipt\b",
    ]
    pii_terms = [
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?){1}\d{3}[-.\s]?\d{4}\b",
    ]

    for path in sample_files:
        abs_path = os.path.join(ROOT, path)
        if not os.path.exists(abs_path):
            continue
        errors.extend(scan_sample_file(abs_path, enforcement_terms))

    errors.extend(scan_pii([ROOT], pii_terms))
    errors.extend(scan_banned_filenames([ROOT]))
    errors.extend(scan_schema_drift())

    if errors:
        print("\n".join(errors))
        return 1
    print("Dataset physics checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
