# Decisions

Conservative choices made without feedback, newest last. Dates are absolute.

## 2026-09-05 — scaffold

- **Package layout.** The package lives at top-level `cpp_swe_bench/` (uv `module-root = ""`),
  matching the layout table in README.md, rather than `src/cpp_swe_bench/`.
- **Upstream clones live in `./repos/` (git-ignored)**, not `~/repos/` as the original README said.
  README updated. API caches for later repositories go under `repos/cache/`.
- **Runtime dependencies: none.** git is driven via `subprocess`; JSON, regex, argparse from stdlib.
- **Hooks.** `no-commit-to-branch` deliberately not enabled (we commit to main). Large-file limit
  is 50 MB (`--maxkb=51200`). pytest runs as a local `language: system` hook via `uv run`.
- **Timestamps.** `created_at` is git's `%aI` verbatim; git prints UTC as `...Z`, which is valid
  ISO-8601 and is accepted by `validate()`. Not normalised to `+00:00`.
- **`--since` semantics.** Passed straight to `git log --since`, which filters on *committer*
  date, while `created_at` records the *author* date. So a few instances may carry an author
  date earlier than `--since`. Accepted for v0; consumers doing temporal splits should split on
  `created_at`, not on the run's `--since`.
- **Revert detection** is textual: subject starting with `Revert` or a body line starting with
  `This reverts commit`. No SHA verification.
- **Trailer stripping** removes matching lines anywhere in the message, not only in the final
  trailer block, and treats any `<Word>-by:` key as a trailer. Continuation lines of trailers
  (rare, indented) are not stripped.
- **Test-path heuristic** is by directory name (`test`, `tests`, `testing`, `selftests`,
  `unittest(s)`) and by a `test` token in the file name delimited by `_`, `-`, `.` or the
  ends of the name. `kernel/latest.c` and `mm/contest.c` are not test paths.
- **Gold files** exclude test paths rather than dropping the commit: a fix touching
  `mm/x.c` plus a selftest yields `gold_files == ["mm/x.c"]`. The total number of changed
  files is kept in `metadata.changed_files_total` so this can be revisited.
- **Blob fetching.** Patches need contents, so after filtering we collect the pre/post blob ids
  from `git diff-tree` (tree-only, no fetch) and bulk-fetch them with the same
  `git fetch --stdin --filter=blob:none` command git's own lazy fetch uses, in batches of
  5000, before running `git diff`. This avoids one round trip per instance.
- **instance_id** uses the first 12 hex characters of the fix SHA.
