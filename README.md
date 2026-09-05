# Cpp-SWE-bench

Temporally controlled **code localization** instances mined from the git history of large C/C++ repositories.

## Motivation

Most benchmarks for issue-driven code localization (SWE-bench, SWE-bench Lite/Verified, Loc-Bench) are Python-only. The few C/C++ instances that exist (e.g. the C/C++ subset of Multi-SWE-bench) are small, drawn from mid-sized GitHub projects, and carry file-level labels only. Yet the systems where localization is hardest — operating systems, compilers, databases, browsers — are large native-code repositories with millions of lines, deep directory trees, and long histories.

This repository builds localization datasets for exactly that setting. Each instance asks: *given a natural-language description of a defect and a snapshot of the repository at the time, which files (and, where reliable, which functions) had to change to fix it?*

Design goals:

- **Large native-code repositories.** One dataset per repository, starting with Linux (via `Fixes:` trailers) and LLVM (via GitHub issue references).
- **Temporal control.** Every instance records the fix timestamp and the exact pre-fix commit, so datasets can be split by date and evaluated against models with known training cutoffs.
- **Honest labels.** Gold files come from the actual fixing change, restricted to non-test C/C++ sources. Function-level labels are included only when extraction is verified to be reliable (not yet: `gold_functions` is `null` in v0).
- **Reproducibility.** Extraction is a deterministic pipeline over a pinned commit range; anyone with a clone of the upstream repository can regenerate the data.

## Datasets

| Directory | Upstream | Problem statement | Range | Notes |
|---|---|---|---|---|
| `data/linux/v0/` | `torvalds/linux` | commit message (trailers stripped) | commits since 2026-01-01 | candidates carry a `Fixes: <sha>` trailer |
| `data/llvm/v0/` | `llvm/llvm-project` | GitHub issue title + body | commits since 2025-01-01 | candidates say `Fixes #N` / `Closes #N` / `Resolves <issue url>` |

Each directory holds `instances.jsonl`, `STATS.md` (the filter funnel with counts) and `COMMAND.txt` (exact command line, extractor commit, upstream HEAD). Per-repository notes and a leakage probe live in `docs/extraction-<repo>.md`; every judgment call is logged in `docs/decisions.md`.

## Instance schema

One JSON object per line (`data/<repo>/<version>/instances.jsonl`).

| Field | Type | Description |
|---|---|---|
| `instance_id` | str | `<repo>__<short-fix-sha>` — stable, unique |
| `repo` | str | Upstream identifier, e.g. `torvalds/linux` |
| `base_commit` | str | Full SHA of the snapshot to localize in (parent of the fix) |
| `fix_commit` | str | Full SHA of the fixing commit |
| `created_at` | str | ISO-8601 author timestamp of the fix commit |
| `problem_statement` | str | Natural-language defect description (issue report, or commit message with trailers stripped) |
| `problem_source` | str | Where `problem_statement` came from (`github_issue`, `commit_message`, …) |
| `gold_files` | list[str] | Repo-relative paths of non-test C/C++ source files changed by the fix |
| `gold_functions` | list[str] \| null | `path::function` labels; `null` when not extracted |
| `patch` | str | Unified diff of the fix restricted to `gold_files` |
| `metadata` | object | Extractor version, referenced issue/bug IDs, filter decisions |

Fields beyond `metadata` are frozen per dataset version; additions go into `metadata` until the next version. In v0 `metadata` contains `extractor_version`, `references` (the `Fixes:` SHA prefixes or issue numbers as written in the commit message), `filters` (the funnel stages applied), `changed_files_total` (all files the fix touched, including non-gold ones) and, for issue-backed instances, `issue_number` and `issue_url`.

## Filters

Applied in this order; `STATS.md` reports survivors of each stage.

1. not a merge commit
2. not a revert (`Revert "..."` subject or `This reverts commit` body)
3. has a reference (`Fixes: <sha>` trailer for Linux; `Fixes/Closes/Resolves #N` for GitHub-issue repositories)
4. at least one gold file: changed path with a C/C++ extension (`.c .h .cc .cpp .cxx .hh .hpp .hxx`) that is not a test path (`test/`, `tests/`, `testing/`, `selftests/`, `unittest(s)/` directories, or a `test` token in the file name)
5. between 1 and 5 gold files
6. a non-empty problem statement (for issue-backed repositories: the first referenced number that is a real issue, not a pull request or a deleted issue)

## Repository layout

```
cpp_swe_bench/      extraction library: gitutil, filters, schema, writers, extract, github
scripts/            extract.py, validate.py, leakage.py
data/<repo>/<ver>/  instances.jsonl + STATS.md + COMMAND.txt
tests/              unit tests on synthetic git repos created in tmp_path; no network
docs/               decisions.md and per-repository extraction notes
repos/              local upstream clones and the GitHub API cache (git-ignored)
```

## Setup

Requires Python 3.14 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run pre-commit install
uv run pytest
```

Upstream repositories are cloned into `repos/<name>` (git-ignored). Blob-less clones are sufficient; blobs for the surviving instances are bulk-fetched when patches are produced.

```bash
git clone --filter=blob:none --no-checkout https://github.com/torvalds/linux.git repos/linux
git clone --filter=blob:none --no-checkout https://github.com/llvm/llvm-project.git repos/llvm
git -C repos/linux config gc.auto 0 && git -C repos/llvm config gc.auto 0
```

Do not run status-style git commands (or leave an editor/shell) inside a `--no-checkout` partial clone: anything that diffs HEAD against the empty index fetches every blob in HEAD.

## Regenerating a dataset

```bash
uv run python scripts/extract.py --repo linux --since 2026-01-01 --out data/linux/v0/
GITHUB_TOKEN=... uv run python scripts/extract.py --repo llvm --since 2025-01-01 --out data/llvm/v0/
uv run python scripts/validate.py data/linux/v0/instances.jsonl
uv run python scripts/leakage.py data/linux/v0/instances.jsonl --n 20
```

`--since` is passed to `git log` (committer date). Issue-backed repositories read `GITHUB_TOKEN` if set (5,000 requests/hour) and otherwise run unauthenticated at 60 requests/hour; responses are cached under `repos/cache/` so re-runs are offline. `--no-patch` skips patch generation for a quick funnel count.

## Non-goals

- Executable test harnesses (build/run-the-tests style evaluation). This is a localization dataset, not a repair benchmark.
- Curating "clean" issues by hand. Filters are programmatic and documented; nothing is edited manually.

## License

Code in this repository is MIT-licensed. Extracted data inherits the license of the respective upstream project; commit messages and issue texts remain the property of their authors.
