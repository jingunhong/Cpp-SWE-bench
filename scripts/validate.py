"""Re-validate every line of an instances.jsonl against the schema.

uv run python scripts/validate.py data/linux/v0/instances.jsonl
"""

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cpp_swe_bench.schema import Instance  # noqa: E402


def main() -> None:
    path = Path(sys.argv[1])
    total, bad, ids = 0, 0, Counter()
    problems: Counter[str] = Counter()
    with path.open(encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            total += 1
            try:
                inst = Instance.from_json(line)
                errors = inst.validate()
                ids[inst.instance_id] += 1
            except (TypeError, ValueError) as e:
                errors = [f"unparseable: {e}"]
            if errors:
                bad += 1
                problems.update(errors)
                print(f"line {lineno}: {'; '.join(errors)}", file=sys.stderr)
    dupes = sum(1 for n in ids.values() if n > 1)
    print(f"{total} instances, {total - bad} valid, {bad} invalid, {dupes} duplicate ids")
    for problem, n in problems.most_common():
        print(f"  {n}x {problem}")
    sys.exit(1 if bad or dupes else 0)


if __name__ == "__main__":
    main()
