import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

SYSTEM_PLACEHOLDER = "<SYSTEM_PROMPT_FROM_BLUX_CA>"
CLASSIFICATIONS = ["Struggler", "Indulger", "Unclear"]


def parse_args():
    parser = argparse.ArgumentParser(description="Summarize BLUX-cA dataset JSONL files")
    parser.add_argument("paths", nargs="*", help="Files or directories to summarize. Defaults to data/*.jsonl")
    parser.add_argument("--top", type=int, default=5, help="Number of top repeated user prompts to display")
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


def summarize_file(path: Path, top_n: int):
    classification_counter = Counter()
    audit_count = 0
    user_counter = Counter()
    total = 0

    with path.open(encoding="utf-8") as f:
        for idx, line in enumerate(f, 1):
            obj = json.loads(line)
            total += 1
            messages = obj.get("messages", [])
            if len(messages) >= 2:
                user_text = messages[1].get("content", "").strip()
                if user_text:
                    user_counter[user_text] += 1
            if len(messages) >= 3:
                assistant_text = messages[2].get("content", "")
                if "## Audit Notes" in assistant_text:
                    audit_count += 1
                for classification in CLASSIFICATIONS:
                    marker = f"classification: {classification}"
                    if marker in assistant_text:
                        classification_counter[classification] += 1

    print(f"\n{path} :: {total} examples")
    for classification in CLASSIFICATIONS:
        print(f" - {classification}: {classification_counter[classification]}")
    print(f" - with Audit Notes: {audit_count}")

    print(" - Top repeated user prompts:")
    for text, count in user_counter.most_common(top_n):
        preview = text if len(text) < 120 else text[:117] + "..."
        print(f"    [{count}] {preview}")


def main():
    args = parse_args()
    files = collect_files(args.paths)
    if not files:
        print("No files to summarize.")
        return

    for file in files:
        summarize_file(file, args.top)


if __name__ == "__main__":
    main()
