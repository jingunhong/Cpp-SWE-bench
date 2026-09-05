"""Leakage probe: how many sampled problem statements name a gold file or function verbatim.

uv run python scripts/leakage.py data/linux/v0/instances.jsonl --n 20 --seed 0
"""

import argparse
import json
import random
import re
from pathlib import Path

_HUNK_FUNC_RE = re.compile(r"^@@ .* @@.*?\b([A-Za-z_]\w*)\s*\(", re.MULTILINE)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("jsonl", type=Path)
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    rows = [json.loads(line) for line in args.jsonl.open(encoding="utf-8")]
    sample = random.Random(args.seed).sample(rows, min(args.n, len(rows)))
    path_hits = base_hits = func_hits = 0
    print("| instance_id | full path | basename | function |")
    print("|---|:-:|:-:|:-:|")
    for r in sample:
        text = r["problem_statement"]
        p = any(g in text for g in r["gold_files"])
        b = any(g.rsplit("/", 1)[-1] in text for g in r["gold_files"])
        funcs = set(_HUNK_FUNC_RE.findall(r["patch"]))
        f = any(re.search(rf"\b{re.escape(fn)}\b", text) for fn in funcs)
        path_hits, base_hits, func_hits = path_hits + p, base_hits + b, func_hits + f
        cells = " | ".join("x" if hit else "" for hit in (p, b, f))
        print(f"| {r['instance_id']} | {cells} |")
    n = len(sample)
    print(f"\n{n} sampled: full path {path_hits}, basename {base_hits}, function name {func_hits}")


if __name__ == "__main__":
    main()
