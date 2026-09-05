"""Leakage report: how many problem statements name a gold file or patched function verbatim.

uv run python scripts/leakage.py data/linux/v1/instances*.jsonl          # whole set
uv run python scripts/leakage.py data/linux/v0/instances.jsonl --n 20    # sampled table
"""

import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cpp_swe_bench import leakage  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("jsonl", type=Path, nargs="+")
    ap.add_argument("--n", type=int, default=0, help="sample size; 0 = all instances")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    rows = [json.loads(line) for p in args.jsonl for line in p.open(encoding="utf-8")]
    if args.n:
        rows = random.Random(args.seed).sample(rows, min(args.n, len(rows)))
    hits = dict.fromkeys(leakage.FLAGS, 0)
    for r in rows:
        f = r["metadata"].get("leakage") or leakage.flags(
            r["problem_statement"], r["gold_files"], r["patch"]
        )
        for k in hits:
            hits[k] += bool(f[k])
        if args.n:
            cells = " | ".join("x" if f[k] else "" for k in hits)
            print(f"| {r['instance_id']} | {cells} |")
    n = len(rows)
    print(f"\n{n} instances:")
    for k, v in hits.items():
        print(f"  {k}: {v} ({100 * v / n:.1f}%)")


if __name__ == "__main__":
    main()
