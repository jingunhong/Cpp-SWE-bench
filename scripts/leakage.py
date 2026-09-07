"""Leakage report: how many texts name a gold file or patched function verbatim.

uv run python scripts/leakage.py data/linux/v2/instances*.jsonl          # whole set
uv run python scripts/leakage.py data/linux/v2/instances.jsonl --n 20    # sampled table

Reports ``problem_statement`` over the instances that have one and ``commit_message`` over
all instances (v2); older files without ``commit_message`` report the statement only.
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
    texts = {"problem_statement": "leakage", "commit_message": "commit_message_leakage"}
    for field, key in texts.items():
        hits = dict.fromkeys(leakage.FLAGS, 0)
        n = 0
        for r in rows:
            if field not in r or r[field] is None:
                continue
            f = r["metadata"].get(key) or leakage.flags(r[field], r["gold_files"], r["patch"])
            n += 1
            for k in hits:
                hits[k] += bool(f[k])
            if args.n:
                cells = " | ".join("x" if f[k] else "" for k in hits)
                print(f"| {r['instance_id']} | {cells} |")
        if not n:
            continue
        print(f"\n{field}, {n} instances:")
        for k, v in hits.items():
            print(f"  {k}: {v} ({100 * v / n:.1f}%)")


if __name__ == "__main__":
    main()
