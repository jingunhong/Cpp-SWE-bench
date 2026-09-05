"""Thin ``git`` subprocess wrappers.

Everything here works on a blob-less clone (``git clone --filter=blob:none``)
without triggering lazy blob fetches, except :func:`diff` and
:func:`prefetch_blobs`, which need file contents.
"""

import subprocess
from dataclasses import dataclass
from pathlib import Path

_RS, _FS = "\x1e", "\x1f"
_FORMAT = f"{_RS}%H{_FS}%P{_FS}%aI{_FS}%B{_FS}"


@dataclass
class Commit:
    sha: str
    parents: list[str]
    author_date: str
    message: str
    files: list[str]  # changed paths vs. first parent; empty unless requested


def run(repo: Path, *args: str, input: str | None = None) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
        input=input,
    ).stdout


def log(repo: Path, *, since: str | None = None, rev: str = "HEAD", files: bool = False):
    """Yield commits reachable from ``rev`` in ``git log`` order.

    ``files=True`` adds the name-only diff against the first parent in the same
    pass (one git process for the whole history instead of one per commit).
    """
    args = ["log", f"--format={_FORMAT}", "--no-renames"]
    if since:
        args.append(f"--since={since}")
    if files:
        args.append("--name-only")
    args.append(rev)
    out = run(repo, *args)
    for record in out.split(_RS)[1:]:
        sha, parents, date, message, names = record.split(_FS, 4)
        yield Commit(sha, parents.split(), date, message, names.split())


def parents(repo: Path, sha: str) -> list[str]:
    return run(repo, "rev-list", "--parents", "-n1", sha).split()[1:]


def changed_files(repo: Path, base: str, head: str) -> list[str]:
    return run(repo, "diff", "--name-only", "--no-renames", base, head).split("\n")[:-1]


def author_date(repo: Path, sha: str) -> str:
    return run(repo, "log", "-1", "--format=%aI", sha).strip()


def message(repo: Path, sha: str) -> str:
    return run(repo, "log", "-1", "--format=%B", sha)


def diff(repo: Path, base: str, head: str, paths: list[str]) -> str:
    """Unified diff restricted to ``paths``. Fetches missing blobs lazily."""
    return run(repo, "diff", "--no-renames", "--no-color", base, head, "--", *paths)


def blob_oids(repo: Path, base: str, head: str, paths: list[str]) -> list[str]:
    """Pre- and post-image blob ids touched by the diff, without fetching them."""
    raw = run(repo, "diff-tree", "-r", "--no-renames", base, head, "--", *paths)
    oids = []
    for line in raw.splitlines():
        _, _, old, new, _ = line.split(maxsplit=4)
        oids += [o for o in (old, new) if set(o) != {"0"}]
    return oids


def prefetch_blobs(repo: Path, oids: list[str], batch: int = 5000) -> None:
    """Fetch blobs in bulk from the promisor remote (same command git's lazy fetch uses).

    No-op on a full clone.
    """
    if not run(repo, "config", "--default", "", "extensions.partialClone").strip():
        return
    oids = sorted(set(oids))
    for i in range(0, len(oids), batch):
        run(
            repo,
            "-c",
            "fetch.negotiationAlgorithm=noop",
            "fetch",
            "origin",
            "--quiet",
            "--no-tags",
            "--no-write-fetch-head",
            "--recurse-submodules=no",
            "--filter=blob:none",
            "--stdin",
            input="\n".join(oids[i : i + batch]) + "\n",
        )


def head(repo: Path) -> str:
    return run(repo, "rev-parse", "HEAD").strip()
