"""Extract localization instances from a local clone.

uv run python scripts/extract.py --repo linux --since 2022-01-01 --out data/linux/v0/
"""

import argparse
import shlex
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cpp_swe_bench import extract, filters, gitutil, writers  # noqa: E402

REPOS = {
    "linux": {"upstream": "torvalds/linux", "references": filters.fixes_shas},
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, choices=sorted(REPOS))
    ap.add_argument("--since", help="git --since bound (committer date), e.g. 2022-01-01")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--repos-dir", type=Path, default=Path("repos"))
    ap.add_argument("--no-patch", action="store_true", help="skip patches (dry run for counts)")
    args = ap.parse_args()

    clone = args.repos_dir / args.repo
    cfg = REPOS[args.repo]
    funnel: dict[str, int] = {}
    instances = list(
        extract.mine(
            clone,
            args.repo,
            cfg["upstream"],
            since=args.since,
            references=cfg["references"],
            problem=extract.commit_message_problem,
            funnel=funnel,
        )
    )
    print(f"{len(instances)} instances after filters", file=sys.stderr)
    if not args.no_patch:
        extract.add_patches(clone, instances)

    args.out.mkdir(parents=True, exist_ok=True)
    n = writers.write_jsonl(args.out / "instances.jsonl", instances)
    extractor_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()
    upstream_head = gitutil.head(clone)
    writers.write_stats(
        args.out / "STATS.md",
        f"{args.repo} extraction stats",
        list(funnel.items()),
        {
            "instances written": n,
            "upstream": cfg["upstream"],
            "upstream HEAD": upstream_head,
            "since": args.since,
            "extractor commit": extractor_sha,
            "extractor version": extract.EXTRACTOR_VERSION,
        },
    )
    (args.out / "COMMAND.txt").write_text(
        f"command: {shlex.join(sys.argv)}\n"
        f"extractor git SHA: {extractor_sha}\n"
        f"upstream HEAD: {upstream_head}\n"
    )
    print(f"wrote {n} instances to {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
