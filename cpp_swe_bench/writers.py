"""Output writers: ``instances.jsonl`` and ``STATS.md``."""

from collections.abc import Iterable
from pathlib import Path

from .schema import Instance


def write_jsonl(path: Path, instances: Iterable[Instance]) -> int:
    n = 0
    with path.open("w", encoding="utf-8") as f:
        for inst in instances:
            f.write(inst.to_json() + "\n")
            n += 1
    return n


def write_stats(path: Path, title: str, funnel: list[tuple[str, int]], notes: dict) -> None:
    """``funnel`` is an ordered list of (stage, survivors); the first stage is the
    candidate pool every percentage is relative to."""
    total = funnel[0][1] if funnel else 0
    lines = [
        f"# {title}",
        "",
        "| Stage | Survived | % of candidates | Dropped here |",
        "|---|---:|---:|---:|",
    ]
    prev = total
    for stage, count in funnel:
        pct = 100 * count / total if total else 0
        lines.append(f"| {stage} | {count} | {pct:.1f}% | {prev - count} |")
        prev = count
    lines += ["", "## Run", ""] + [f"- **{k}**: {v}" for k, v in notes.items()]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
