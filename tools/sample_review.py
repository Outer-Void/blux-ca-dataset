import argparse
import json
import random
from datetime import date
from pathlib import Path

DEFAULT_SAMPLE = 3
SEED = 20240601


def parse_args():
    parser = argparse.ArgumentParser(description="Create deterministic review samples from JSONL files")
    parser.add_argument("paths", nargs="*", help="Files or directories to sample. Defaults to data/*.jsonl")
    parser.add_argument("--n", type=int, default=DEFAULT_SAMPLE, help="Samples per file")
    parser.add_argument("--seed", type=int, default=SEED, help="Random seed for reproducibility")
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


def sample_file(path: Path, n: int, rng: random.Random):
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        return []
    indices = list(range(len(lines)))
    rng.shuffle(indices)
    chosen = sorted(indices[: min(n, len(lines))])
    samples = []
    for idx in chosen:
        obj = json.loads(lines[idx])
        user = obj.get("messages", [{} ,{}])[1].get("content", "") if obj.get("messages") else ""
        assistant = obj.get("messages", [{}, {}, {}])[2].get("content", "") if obj.get("messages") else ""
        samples.append((idx + 1, user, assistant))
    return samples


def main():
    args = parse_args()
    rng = random.Random(args.seed)
    files = collect_files(args.paths)
    if not files:
        print("No files to sample.")
        return

    review_dir = Path("review")
    review_dir.mkdir(exist_ok=True)
    out_path = review_dir / f"sample_{date.today().isoformat()}.md"

    with out_path.open("w", encoding="utf-8") as out:
        out.write("# BLUX-cA Dataset Sample Review\n")
        out.write(f"Seed: {args.seed} | Samples per file: {args.n}\n\n")
        for path in files:
            out.write(f"## {path}\n")
            samples = sample_file(path, args.n, rng)
            if not samples:
                out.write("No data found.\n\n")
                continue
            for line_no, user, assistant in samples:
                out.write(f"- Line {line_no}:\n  - user: {user}\n  - assistant: {assistant[:400]}\n")
            out.write("\n")

    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
