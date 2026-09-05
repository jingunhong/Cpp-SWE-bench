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

## 2026-09-05 — Linux v0 run

- **Shell working directory must stay outside the clone.** The tooling around this session runs
  `git diff --cached --shortstat` in the shell's current directory; inside a `--no-checkout`
  partial clone that command needs every blob in HEAD and pulled 293 MB (95,380 blobs) twice
  before it was traced. The extractor itself was verified tree-only: a name-only log over
  412k commits fetched nothing.
- **Auto-gc disabled on clones** (`git config gc.auto 0` in `repos/linux` and `repos/llvm`).
  Lazy fetches create one pack each; the first run hit `gc.autoPackLimit` and a background
  repack of the 2 GB clone stalled every `git diff` for minutes.
- **Prefetch guard** checks `remote.origin.promisor == true`; `extensions.partialClone` is
  not set by current git for `--filter` clones.
- **`--since 2026-01-01`, not 2022-01-01.** The full range since 2022 yields 63,115 instances
  (~190 MB with patches); the 50 MB limit allows ~15k instances at the measured ~3 KB per
  instance, and 2026-01-01 is the earliest month boundary that fits. Funnel counts for the
  full 2022+ range are recorded in `docs/extraction-linux.md` for reference.
- **`Fixes:` reference is not resolved.** `metadata.references` stores the SHA prefixes as
  written in the trailer (7–40 hex chars); they are not verified to exist.
- **Multiple `Fixes:` trailers** keep the commit as one instance listing all references.

## 2026-09-05 — LLVM v0 run

- **Repository choice: llvm/llvm-project.** Compiler, C++-heavy, and since the 2021 move to
  GitHub issues commits carry `Fixes #N` / `Fixes <issue url>` / `Closes #N` lines
  (~10k such commits since 2024). ClickHouse references issues mostly in PR merge commits;
  Godot is smaller. Not benchmarked further.
- **`--since 2025-01-01`.** 5,924 git-side survivors versus 8,632 for 2024+, chosen to keep
  the first API pass around one hour at the authenticated 5,000 requests/hour limit.
- **Token.** `GITHUB_TOKEN` was not set. `gh` on this machine is logged in, so the run was
  started with `GITHUB_TOKEN="$(gh auth token)"` (the user's own account, read-only public
  issue reads). The extractor only ever reads the `GITHUB_TOKEN` environment variable.
- **Issue resolution.** The first referenced number that resolves to a real issue is used;
  numbers that are pull requests or 404 are skipped and counted under
  `problem statement drops` in STATS.md. A commit whose references are all PRs is dropped.
- **Responses cached** as raw JSON under `repos/cache/llvm__llvm-project/<n>.json` (404s cached
  as `null`), so re-runs are offline.
- **Problem statement = issue title + body verbatim** (Markdown, including any code blocks and
  stack traces). No scrubbing in v0; see the leakage note.
- **Transient API failures are retried** (up to 8 attempts, exponential backoff) for
  connection drops, timeouts and 5xx responses; 403/429 sleep until the quota resets; any
  other HTTP error aborts the run. The first LLVM run died on a `RemoteDisconnected` after
  562 issues; the cache made the restart free.
