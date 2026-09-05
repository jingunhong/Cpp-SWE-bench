# Cpp-SWE-bench

Temporally controlled **code localization** instances mined from the git history of large C/C++ repositories.

## Motivation

Most benchmarks for issue-driven code localization (SWE-bench, SWE-bench Lite/Verified, Loc-Bench) are Python-only. The few C/C++ instances that exist (e.g. the C/C++ subset of Multi-SWE-bench) are small, drawn from mid-sized GitHub projects, and carry file-level labels only. Yet the systems where localization is hardest — operating systems, compilers, databases, browsers — are large native-code repositories with millions of lines, deep directory trees, and long histories.

This repository builds localization datasets for exactly that setting. Each instance asks: *given a natural-language description of a defect and a snapshot of the repository at the time, which files (and, where reliable, which functions) had to change to fix it?*

Design goals:

- **Large native-code repositories.** One dataset per repository, starting with Linux (via `Fixes:` trailers) and extending to large C++ projects with traceable issue↔commit links.
- **Temporal control.** Every instance records the fix timestamp and the exact pre-fix commit, so datasets can be split by date and evaluated against models with known training cutoffs.
- **Honest labels.** Gold files come from the actual fixing change, restricted to non-test C/C++ sources. Function-level labels are included only when extraction is verified to be reliable.
- **Reproducibility.** Extraction is a deterministic pipeline over a pinned commit range; anyone with a clone of the upstream repository can regenerate the data.

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

Fields beyond `metadata` are frozen per dataset version; additions go into `metadata` until the next version.

## Repository layout

```
cpp_swe_bench/      extraction library (git mining, filters, schema, writers)
scripts/            entry points: extract, filter, stats, validate
data/<repo>/<ver>/  instances.jsonl + STATS.md + the exact command that produced them
tests/              unit tests on small fixtures; no network, no full clones
docs/               design notes and per-repository extraction decisions
```

## Setup

Requires Python 3.14 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run pre-commit install
uv run pytest
```

Upstream repositories are cloned outside this repo (default `~/repos/<name>`) and are never committed. Blob-less clones (`git clone --filter=blob:none`) are sufficient for file-level extraction.

## Regenerating a dataset

```bash
uv run python scripts/extract.py --repo linux --since 2020-01-01 --out data/linux/v0/
uv run python scripts/validate.py data/linux/v0/instances.jsonl
```

Each `data/<repo>/<ver>/` directory contains the exact command line and upstream HEAD used, so the run is reproducible.

## Non-goals

- Executable test harnesses (build/run-the-tests style evaluation). This is a localization dataset, not a repair benchmark.
- Curating "clean" issues by hand. Filters are programmatic and documented; nothing is edited manually.

## License

Code in this repository is MIT-licensed. Extracted data inherits the license of the respective upstream project; commit messages and issue texts remain the property of their authors.

