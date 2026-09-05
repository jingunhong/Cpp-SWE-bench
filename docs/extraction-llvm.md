# LLVM extraction (v0)

Upstream: `llvm/llvm-project`, blob-less clone at `repos/llvm`. Candidates are non-merge,
non-revert commits whose message references an issue of `llvm/llvm-project` with
`Fixes/Closes/Resolves #N`, the full issue URL, or `llvm/llvm-project#N` (references to other
repositories such as `clangd/clangd` are ignored). The problem statement is the issue title
plus body from the GitHub REST API (`problem_source = "github_issue"`); everything else
follows the Linux pipeline: `base_commit` is the first parent, `created_at` the author
date, `gold_files` the changed non-test C/C++ sources, `gold_functions` `null`.

## Range

`--since 2025-01-01` (committer date); upstream HEAD and the exact command are in
`data/llvm/v0/COMMAND.txt`. A dry count for `--since 2024-01-01` gave 8,632 git-side
survivors versus 5,924 for 2025-01-01; the shorter range was chosen to keep the first API
pass around an hour. See `docs/decisions.md`.

## GitHub API

- Endpoint `GET /repos/llvm/llvm-project/issues/{n}`; the same endpoint also returns pull
  requests (with a `pull_request` key), which are skipped. The first referenced number that
  is a real issue wins; a commit whose references are all PRs or deleted is dropped and
  counted under `problem statement drops` in `STATS.md`.
- Responses are cached verbatim under `repos/cache/llvm__llvm-project/<n>.json` (`null` for
  404), so a re-run with the same clone and cache is offline and deterministic.
- The run used a token from `GITHUB_TOKEN` (5,000 requests/hour). Unauthenticated runs are
  supported but pause one second per request and sleep through quota exhaustion.

## Results

(filled in from `data/llvm/v0/STATS.md` after the run)

## Leakage note

(filled in from `scripts/leakage.py`)
