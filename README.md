# Cpp-SWE-bench

Temporally controlled **code localization** instances mined from the git history of large C/C++ repositories.

## Motivation

Most benchmarks for issue-driven code localization (SWE-bench, SWE-bench Lite/Verified, Loc-Bench) are Python-only. The few C/C++ instances that exist (e.g. the C/C++ subset of Multi-SWE-bench) are small, drawn from mid-sized GitHub projects, and carry file-level labels only. Yet the systems where localization is hardest — operating systems, compilers, databases, browsers — are large native-code repositories with millions of lines, deep directory trees, and long histories.

This repository builds localization datasets for exactly that setting. Each instance asks: *given a natural-language description of a defect and a snapshot of the repository at the time, which files (and, where reliable, which functions) had to change to fix it?*

Design goals:

- **Large native-code repositories.** One dataset per repository: Linux, QEMU and PostgreSQL via commit-message trailers; LLVM, systemd and ClickHouse via GitHub issue references.
- **Temporal control.** Every instance records the fix timestamp and the exact pre-fix commit, so datasets can be split by date and evaluated against models with known training cutoffs.
- **Honest labels.** Gold files come from the actual fixing change, restricted to non-test C/C++ sources. Function-level labels are included only when extraction is verified to be reliable (not yet: `gold_functions` is `null` in v0).
- **Reproducibility.** Extraction is a deterministic pipeline over a pinned commit range; anyone with a clone of the upstream repository can regenerate the data.

## Datasets

| Directory | Upstream | Problem statement | Range | Instances | Notes |
|---|---|---|---|---:|---|
| `data/linux/v0/` | `torvalds/linux` | commit message (trailers stripped) | commits since 2026-01-01 | 14,918 | candidates carry a `Fixes: <sha>` trailer |
| `data/linux/v1/` | `torvalds/linux` | commit message (trailers stripped) | commits since 2022-01-01 | 63,115 | v0 rules, full range, sharded, `metadata.leakage` |
| `data/qemu/v0/` | `qemu/qemu` | commit message (trailers stripped) | commits since 2022-01-01 | 2,367 | candidates carry a `Fixes: <sha>` trailer |
| `data/postgres/v0/` | `postgres/postgres` | commit message (trailers stripped) | commits since 2022-01-01 | 1,333 | candidates carry a `Reported-by:` or `Bug: #N` trailer |
| `data/llvm/v0/` | `llvm/llvm-project` | GitHub issue title + body | commits since 2025-01-01 | 5,794 | candidates say `Fixes #N` / `Closes #N` / `Resolves <issue url>` |
| `data/llvm/v1/` | `llvm/llvm-project` | GitHub issue title + body | commits since 2024-01-01 | 8,357 | v0 rules, full range, two shards, `metadata.leakage` |
| `data/systemd/v0/` | `systemd/systemd` | GitHub issue title + body | commits since 2022-01-01 | 1,418 | candidates reference a systemd issue |
| `data/clickhouse/v0/` | `ClickHouse/ClickHouse` | GitHub issue title + body | commits since 2022-01-01 | 1,022 | candidates reference a ClickHouse issue |
| `data/postgres/v2/` | `postgres/postgres` | archive message (1,318) or `null` | commits since 2022-01-01 | 1,333 | v2 schema; `BUG #` message of the `Discussion:` thread, else its first message |
| `data/qemu/v2/` | `qemu/qemu` | GitLab issue (677) or `null` | commits since 2022-01-01 | 2,821 | v2 schema; GitLab issue URLs are a candidate signal too |
| `data/llvm/v2/` | `llvm/llvm-project` | GitHub issue (8,357) or `null` | commits since 2024-01-01 | 8,504 | v2 schema, v1 range and cache, two shards |
| `data/systemd/v2/` | `systemd/systemd` | GitHub issue (1,418) or `null` | commits since 2022-01-01 | 1,424 | v2 schema, v0 range and cache |
| `data/clickhouse/v2/` | `ClickHouse/ClickHouse` | GitHub issue (1,022) or `null` | commits since 2022-01-01 | 1,049 | v2 schema, v0 range and cache |

v2 directories (schema below) hold the original report in `problem_statement` and the commit message in `commit_message`; the count in parentheses is the number of instances with a report, the rest carry `null`. Each directory holds `instances.jsonl` (or `instances-000.jsonl`, `instances-001.jsonl`, … when one file would exceed 45 MB; read them with a glob), `STATS.md` (the filter funnel with counts) and `COMMAND.txt` (exact command line, extractor commit, upstream HEAD). Per-repository notes and a leakage probe live in `docs/extraction-<repo>.md`; every judgment call is logged in `docs/decisions.md`.

## Instance schema

One JSON object per line (`data/<repo>/<version>/instances.jsonl`).

| Field | Type | Description |
|---|---|---|
| `instance_id` | str | `<repo>__<short-fix-sha>` — stable, unique |
| `repo` | str | Upstream identifier, e.g. `torvalds/linux` |
| `base_commit` | str | Full SHA of the snapshot to localize in (parent of the fix) |
| `fix_commit` | str | Full SHA of the fixing commit |
| `created_at` | str | ISO-8601 author timestamp of the fix commit |
| `problem_statement` | str \| null | The original bug report (title + body) when the repository's history links to one; `null` otherwise (v2) |
| `problem_source` | str \| null | Where the report came from: `github_issue`, `gitlab_issue`, `syzbot`, `lore_report`, `kernel_bugzilla`, `pgsql_archive`; `null` exactly when `problem_statement` is `null` (v2) |
| `commit_message` | str | The fix's commit message with trailers stripped; always present (v2) |
| `gold_files` | list[str] | Repo-relative paths of non-test C/C++ source files changed by the fix |
| `gold_functions` | list[str] \| null | `path::function` labels; `null` when not extracted |
| `patch` | str | Unified diff of the fix restricted to `gold_files` |
| `metadata` | object | Extractor version, referenced issue/bug IDs, filter decisions |

Fields beyond `metadata` are frozen per dataset version; additions go into `metadata` until the next version.

**v2 semantics.** `problem_statement` holds the original report *only*. A commit message is written by the fixer after the fix and describes diagnosis and solution, which is a different and easier localization task than the report; the dataset never presents one as the other. When no report is linked from the commit (or the link does not resolve), the instance is kept with `problem_statement: null` and `problem_source: null`; whether to fall back to `commit_message` at training time is the consumer's decision. In v0/v1, `problem_statement` was the commit message for Linux, QEMU and PostgreSQL (`problem_source = "commit_message"`); v2 moves that text to `commit_message`.

`metadata` contains:

- `extractor_version`, `filters` (the funnel stages applied), `changed_files_total` (all files the fix touched, including non-gold ones);
- `references`: what made the commit a candidate (`Fixes:` SHA prefixes, GitLab issue URLs, issue numbers, or PostgreSQL bug numbers / `Discussion:` URLs as written);
- `report_refs` (v2): the report links found in the commit message, grouped by kind and stored even when fetching fails, so yield can be measured offline. Keys are the source names above plus fetcher-less kinds `link` (`Link:` URLs), `launchpad` (QEMU Launchpad bug URLs) and `pgsql_bug` (`#N` from `Bug: #N`);
- `report_url` (v2) for instances with a report, plus `issue_number` and `issue_url` for `github_issue`;
- `leakage`: `{path, basename, function}` computed against `problem_statement` (whether it names a gold path, a gold basename, or a function from the patch's hunk headers verbatim); `null` when `problem_statement` is `null` (v1+);
- `commit_message_leakage` (v2): the same three flags computed against `commit_message`. The two are never mixed; `STATS.md` reports each over its own denominator.

## Filters

Applied in this order; `STATS.md` reports survivors of each stage.

1. not a merge commit
2. not a revert (`Revert "..."` subject or `This reverts commit` body)
3. has a reference (`Fixes: <sha>` trailer for Linux; `Fixes: <sha>` or a `gitlab.com/qemu-project/qemu/-/issues/N` URL for QEMU; `Reported-by:` or `Bug: #N` trailer for PostgreSQL; `Fixes/Closes/Resolves #N` or the issue URL for GitHub-issue repositories)
4. at least one gold file: changed path with a C/C++ extension (`.c .h .cc .cpp .cxx .hh .hpp .hxx`) that is not a test path (`test/`, `tests/`, `testing/`, `selftests/`, `unittest(s)/` directories, or a `test` token in the file name)
5. between 1 and 5 gold files

Having a report is not a filter (v2): every survivor is written, with `problem_statement: null` when no report resolves. `STATS.md` reports, per source, how many instances carry a report ref, how many resolved, and every failed ref under `report drops`.

## Report sources (v2)

Reports are fetched after the git filters, in the order listed; the first ref that resolves to a real report wins. Raw responses are cached under `repos/cache/<source>/` (404 as `null`), so a re-run with a warm cache is offline.

| Repository | `problem_source` | Ref in the commit message | Fetched from |
|---|---|---|---|
| Linux | `syzbot` | `syzbot+<hash>@syzkaller.appspotmail.com`, `syzkaller.appspot.com/bug?extid=…` | `bug?extid=<hash>&json=1`: bug title + first crash report text |
| Linux | `lore_report` | `Closes: https://lore.kernel.org/…` (or lkml.kernel.org) | `lore.kernel.org/all/<msgid>/raw`: subject + body, quotes and signature stripped; `[PATCH …]` targets are dropped |
| Linux | `kernel_bugzilla` | `bugzilla.kernel.org/show_bug.cgi?id=N` | REST `/rest/bug/N` summary + first comment |
| QEMU | `gitlab_issue` | `gitlab.com/qemu-project/qemu/-/issues/N` (any trailer) | GitLab API v4, no auth: title + description |
| PostgreSQL | `pgsql_archive` | `Discussion:` URL (`postgr.es/m/<msgid>`, `postgresql.org/message-id/…`) | `/message-id/flat/<msgid>`: the thread's `BUG #` message, else its first message; subject + body, quotes and signature stripped |
| LLVM, systemd, ClickHouse | `github_issue` | `Fixes/Closes/Resolves #N`, issue URL, `owner/repo#N` | GitHub REST: title + body (pull requests and deleted issues are drops) |

`Link:` is never a report source (it is usually the patch's own submission link); it is recorded in `metadata.report_refs.link` only, as are QEMU Launchpad URLs (`launchpad`) and PostgreSQL bug numbers (`pgsql_bug`).

## Repository layout

```
cpp_swe_bench/      extraction library: gitutil, filters, schema, writers, extract, reports
scripts/            extract.py, validate.py, leakage.py
data/<repo>/<ver>/  instances.jsonl + STATS.md + COMMAND.txt
tests/              unit tests on synthetic git repos created in tmp_path; no network
docs/               decisions.md and per-repository extraction notes
repos/              local upstream clones and the report caches (git-ignored)
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
# likewise qemu/qemu, postgres/postgres, systemd/systemd, ClickHouse/ClickHouse into repos/<name>
for r in repos/*/; do git -C "$r" config gc.auto 0; done
```

Do not run status-style git commands (or leave an editor/shell) inside a `--no-checkout` partial clone: anything that diffs HEAD against the empty index fetches every blob in HEAD.

## Regenerating a dataset

```bash
uv run python scripts/extract.py --repo linux --since 2022-01-01 --out data/linux/v2/
uv run python scripts/extract.py --repo qemu --since 2022-01-01 --out data/qemu/v2/
uv run python scripts/extract.py --repo postgres --since 2022-01-01 --out data/postgres/v2/
GITHUB_TOKEN=... uv run python scripts/extract.py --repo llvm --since 2024-01-01 --out data/llvm/v2/
GITHUB_TOKEN=... uv run python scripts/extract.py --repo systemd --since 2022-01-01 --out data/systemd/v2/
GITHUB_TOKEN=... uv run python scripts/extract.py --repo clickhouse --since 2022-01-01 --out data/clickhouse/v2/
uv run python scripts/validate.py data/linux/v2/instances*.jsonl
uv run python scripts/leakage.py data/linux/v2/instances*.jsonl          # whole set, both texts
uv run python scripts/leakage.py data/linux/v2/instances-000.jsonl --n 20    # sampled table
```

`--since` is passed to `git log` (committer date). Issue-backed repositories read `GITHUB_TOKEN` if set (5,000 requests/hour) and otherwise run unauthenticated at 60 requests/hour; the other sources need no credentials and are paced politely. Responses are cached under `repos/cache/<source>/` so re-runs are offline. `--no-patch` skips patch generation and `--no-reports` skips report fetching, for a quick funnel and yield count.

## Non-goals

- Executable test harnesses (build/run-the-tests style evaluation). This is a localization dataset, not a repair benchmark.
- Curating "clean" issues by hand. Filters are programmatic and documented; nothing is edited manually.

## License

Code in this repository is MIT-licensed. Extracted data inherits the license of the respective upstream project; commit messages and issue texts remain the property of their authors.
