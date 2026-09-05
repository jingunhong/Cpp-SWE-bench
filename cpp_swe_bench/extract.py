"""The extraction pipeline: git history -> filtered Instance records + funnel counts."""

from collections.abc import Callable, Iterator
from pathlib import Path

from . import EXTRACTOR_VERSION, filters, gitutil
from .schema import Instance

FILTER_ORDER = ("not merge", "not revert", "has reference", "has gold files", "1-5 gold files")


def mine(
    repo: Path,
    repo_name: str,
    upstream: str,
    *,
    since: str | None,
    references: Callable[[str], list],
    problem: Callable[[gitutil.Commit], tuple[str, str, dict] | None],
    funnel: dict[str, int],
) -> Iterator[Instance]:
    """Yield instances without ``patch`` (filled by :func:`add_patches`).

    ``references(message)`` returns the issue/commit references that make a commit a
    candidate; ``problem(commit)`` returns ``(statement, source, extra_metadata)`` or
    None to drop.
    ``funnel`` is updated in place with survivor counts per stage.
    """
    for stage in ("candidates", *FILTER_ORDER, "has problem statement"):
        funnel.setdefault(stage, 0)
    for c in gitutil.log(repo, since=since, files=True):
        funnel["candidates"] += 1
        if filters.is_merge(c.parents):
            continue
        funnel["not merge"] += 1
        if filters.is_revert(c.message):
            continue
        funnel["not revert"] += 1
        refs = references(c.message)
        if not refs:
            continue
        funnel["has reference"] += 1
        gold = filters.gold_files(c.files)
        if not gold:
            continue
        funnel["has gold files"] += 1
        if not filters.file_count_ok(gold):
            continue
        funnel["1-5 gold files"] += 1
        found = problem(c)
        if not found:
            continue
        funnel["has problem statement"] += 1
        statement, source, extra = found
        yield Instance(
            instance_id=f"{repo_name}__{c.sha[:12]}",
            repo=upstream,
            base_commit=c.parents[0],
            fix_commit=c.sha,
            created_at=c.author_date,
            problem_statement=statement,
            problem_source=source,
            gold_files=gold,
            gold_functions=None,
            patch="",
            metadata={
                "extractor_version": EXTRACTOR_VERSION,
                "references": refs,
                "filters": list(FILTER_ORDER),
                "changed_files_total": len(c.files),
                **extra,
            },
        )


def add_patches(repo: Path, instances: list[Instance]) -> None:
    """Fill ``patch`` for every instance, bulk-fetching blobs first on partial clones."""
    oids = []
    for inst in instances:
        oids += gitutil.blob_oids(repo, inst.base_commit, inst.fix_commit, inst.gold_files)
    gitutil.prefetch_blobs(repo, oids)
    for inst in instances:
        inst.patch = gitutil.diff(repo, inst.base_commit, inst.fix_commit, inst.gold_files)


def commit_message_problem(c: gitutil.Commit) -> tuple[str, str, dict] | None:
    """Problem statement = commit message with trailers stripped."""
    text = filters.strip_trailers(c.message)
    return (text, "commit_message", {}) if text else None
