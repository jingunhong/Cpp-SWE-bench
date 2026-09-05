# systemd extraction (v0)

Upstream: `systemd/systemd`, blob-less clone at `repos/systemd`. Same pipeline as LLVM:
candidates are non-merge, non-revert commits referencing a `systemd/systemd` issue
(`Fixes #N`, `Closes #N`, `Resolves <issue url>`...); the problem statement is the issue
title and body from the GitHub API (`problem_source = "github_issue"`), cached under
`repos/cache/systemd__systemd/`.

## Results (`--since 2022-01-01`, `data/systemd/v0/STATS.md`)

36,174 candidates → 31,169 non-merge → 30,936 non-revert → 2,055 with an issue reference →
1,498 with gold files → 1,424 with 1–5 gold files → **1,418 instances** (7 commits
referenced only pull requests). All validate; one 10.9 MB file. Leakage over the full set:
path 19.9%, basename 22.1%, patched function 15.9%.

## Caveats

- Most systemd fixes arrive through pull requests whose merge commit, not the individual
  commit, names the issue; only 6% of non-merge commits carry a reference. A "take the PR's
  commits when the merge commit references an issue" rule would enlarge this set several
  times over and is the main gap for this repository (and for Godot, DuckDB, ClickHouse).
- systemd issue bodies follow a template (version, distribution, expected/actual behaviour,
  log excerpts); file-path leakage is the highest of the repositories so far because logs
  and backtraces name source files.
