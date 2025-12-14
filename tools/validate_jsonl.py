import argparse
import json
import sys
from pathlib import Path

SYSTEM_PLACEHOLDER = "<SYSTEM_PROMPT_FROM_BLUX_CA>"
CLASSIFICATIONS = {"Struggler", "Indulger", "Unclear"}
EXPECTED_FILES = {
    "core.jsonl",
    "coding.jsonl",
    "governance.jsonl",
    "safety.jsonl",
    "reasoning.jsonl",
    "creation.jsonl",
    "conversation.jsonl",
    "efficiency.jsonl",
    "relationships.jsonl",
}
EXPECTED_COUNT = 500


def parse_args():
    parser = argparse.ArgumentParser(description="Validate BLUX-cA dataset JSONL files")
    parser.add_argument("paths", nargs="*", help="Files or directories to validate. Defaults to data/*.jsonl")
    return parser.parse_args()


def collect_files(raw_paths):
    if not raw_paths:
        return sorted(Path("data").glob("*.jsonl"))

    files = []
    for raw in raw_paths:
        path = Path(raw)
        if path.is_dir():
            files.extend(sorted(path.glob("*.jsonl")))
        elif path.is_file():
            files.append(path)
    return files


def validate_audit_block(text):
    if "## Audit Notes" not in text:
        return True, None

    required_lines = ["- classification:", "- applied:", "- risks:", "- next_step:"]
    for line in required_lines:
        if line not in text:
            return False, f"Audit block missing '{line}'"

    # classification value check
    for segment in text.splitlines():
        if segment.startswith("- classification:"):
            value = segment.split(":", 1)[1].strip()
            if value not in CLASSIFICATIONS:
                return False, f"Invalid classification '{value}' in audit block"
    return True, None


def validate_messages(obj):
    errors = []
    if "messages" not in obj or not isinstance(obj["messages"], list):
        return ["Missing 'messages' list"]
    msgs = obj["messages"]
    if len(msgs) < 3:
        errors.append("Expected at least system, user, assistant messages")
        return errors

    sys_msg, user_msg, assistant_msg = msgs[0], msgs[1], msgs[2]

    if sys_msg.get("role") != "system" or sys_msg.get("content") != SYSTEM_PLACEHOLDER:
        errors.append("First message must be system placeholder")
    if user_msg.get("role") != "user" or not user_msg.get("content", "").strip():
        errors.append("Second message must be non-empty user content")
    if assistant_msg.get("role") != "assistant" or not assistant_msg.get("content", "").strip():
        errors.append("Third message must be non-empty assistant content")

    ok, audit_issue = validate_audit_block(assistant_msg.get("content", ""))
    if not ok:
        errors.append(audit_issue)

    # ensure only allowed roles
    for msg in msgs:
        if msg.get("role") not in {"system", "user", "assistant"}:
            errors.append(f"Invalid role '{msg.get('role')}'")
    return errors


def validate_file(path: Path):
    errors = []
    with path.open(encoding="utf-8") as f:
        lines = f.readlines()

    expected = EXPECTED_COUNT if path.name in EXPECTED_FILES else None
    if expected is not None and len(lines) != expected:
        errors.append(f"Expected {expected} lines, found {len(lines)}")

    for idx, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            errors.append(f"Line {idx}: empty line")
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"Line {idx}: invalid JSON ({exc})")
            continue
        for issue in validate_messages(obj):
            errors.append(f"Line {idx}: {issue}")

    return errors


def main():
    args = parse_args()
    files = collect_files(args.paths)
    if not files:
        print("No files to validate.")
        sys.exit(1)

    overall_errors = {}
    for file in files:
        errs = validate_file(file)
        if errs:
            overall_errors[file] = errs

    if overall_errors:
        for file, errs in overall_errors.items():
            print(f"\nErrors in {file}:")
            for err in errs[:50]:
                print(f" - {err}")
            if len(errs) > 50:
                print(f" ... {len(errs) - 50} more")
        sys.exit(1)

    print("All JSONL files passed validation.")


if __name__ == "__main__":
    main()
