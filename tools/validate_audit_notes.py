import argparse
import json
import sys
from pathlib import Path

SYSTEM_PLACEHOLDER = "<SYSTEM_PROMPT_FROM_BLUX_CA>"
REQUIRED_FIELDS = [
    "- classification:",
    "- applied:",
    "- posture_score:",
    "- detected_patterns:",
    "- next_step:",
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Validate that JSONL samples include Audit Notes with posture score and detected patterns."
    )
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


def parse_posture_score(line):
    try:
        value = line.split(":", 1)[1].strip()
    except IndexError:
        return None
    if not value:
        return None
    try:
        score = int(value)
    except ValueError:
        return None
    if 0 <= score <= 100:
        return score
    return None


def audit_notes_section(text):
    if "## Audit Notes" not in text:
        return None
    lines = text.splitlines()
    start = None
    for idx, line in enumerate(lines):
        if line.strip() == "## Audit Notes":
            start = idx
            break
    if start is None:
        return None
    return lines[start:]


def validate_detected_patterns(lines, start_index):
    line = lines[start_index]
    value = line.split(":", 1)[1].strip() if ":" in line else ""
    if value:
        return True
    for next_line in lines[start_index + 1 :]:
        if next_line.startswith("- "):
            break
        if next_line.strip().startswith("-"):
            return True
        if next_line.strip() and not next_line.startswith(" "):
            break
    return False


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

    content = assistant_msg.get("content", "")
    section = audit_notes_section(content)
    if section is None:
        errors.append("Missing '## Audit Notes' section")
        return errors

    for required in REQUIRED_FIELDS:
        if required not in content:
            errors.append(f"Audit Notes missing '{required}'")

    score_line = None
    for line in section:
        if line.strip().startswith("- posture_score:"):
            score_line = line
            break
    if score_line is None:
        errors.append("Audit Notes missing posture_score value")
    else:
        score = parse_posture_score(score_line)
        if score is None:
            errors.append("Invalid posture_score; must be integer 0-100")

    detected_index = None
    for idx, line in enumerate(section):
        if line.strip().startswith("- detected_patterns:"):
            detected_index = idx
            break
    if detected_index is None:
        errors.append("Audit Notes missing detected_patterns list")
    else:
        if not validate_detected_patterns(section, detected_index):
            errors.append("detected_patterns must include a value or list item")

    for msg in msgs:
        if msg.get("role") not in {"system", "user", "assistant"}:
            errors.append(f"Invalid role '{msg.get('role')}'")

    return errors


def validate_file(path: Path):
    errors = []
    with path.open(encoding="utf-8") as f:
        lines = f.readlines()

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

    print("All JSONL files passed audit-note validation.")


if __name__ == "__main__":
    main()
