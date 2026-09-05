# ClickHouse extraction (v0)

Upstream: `ClickHouse/ClickHouse`, blob-less clone at `repos/clickhouse` (6.7 GB even
without blobs: 200k commits over a large tree). Same pipeline as LLVM: candidates are
non-merge, non-revert commits referencing a `ClickHouse/ClickHouse` issue; the problem
statement is the issue title and body from the GitHub API (`problem_source =
"github_issue"`), cached under `repos/cache/ClickHouse__ClickHouse/`.

## Results (`--since 2022-01-01`, `data/clickhouse/v0/STATS.md`)

198,025 candidates → 132,696 non-merge → 130,560 non-revert → 1,497 with an issue
reference → 1,120 with gold files → 1,049 with 1–5 gold files → **1,022 instances**
(29 commits referenced only pull requests). All validate; one 9.6 MB file. Leakage over
the full set: path 39.0%, basename 42.2%, patched function 27.6%.

## Caveats

- Only 1% of ClickHouse commits reference an issue directly; the link normally sits in the
  pull request body and its merge commit (22k merge subjects since 2024 carry a PR number).
  Walking PR merges is the missing rule, as for systemd, Godot and DuckDB.
- Issue bodies often paste a full stack trace or a fuzzer report naming the source file
  and function, hence the highest path leakage of all repositories (39%).
