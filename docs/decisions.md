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

## 2026-09-05 — leakage and v1

- **Full-set leakage (v0).** Linux: 4.9% of problem statements name a gold path verbatim,
  6.9% a gold basename, 53.0% a function patched by the fix. LLVM: 14.4% path, 23.3%
  basename, 20.9% function.
- **No masking.** Real bug reports name functions and files; rewriting the text would make
  the instances less faithful and the masking itself is another labeling step that can be
  wrong. Instead every instance now carries `metadata.leakage = {path, basename, function}`
  so consumers can filter or stratify, and STATS.md reports the totals. Revisit if an
  evaluation needs a leakage-free subset larger than what filtering leaves.
- **Function-name leakage is measured from hunk headers**, i.e. git's default C/C++
  funcname heuristic on the patch; it is a proxy, not a gold function label.
- **v1 = full ranges + leakage flags, sharded.** `write_jsonl` splits above 45 MB into
  `instances-NNN.jsonl`; readers glob `instances*.jsonl`. Linux v1 covers commits since
  2022-01-01, LLVM v1 since 2024-01-01 (GitHub issues start in late 2021; earlier LLVM
  commits reference Bugzilla, which the pipeline does not read). Schema unchanged.
- **v0 is kept as is**; it is a strict subset range of v1 without the flags.
- **`git log --since` is not exactly reproducible at the boundary.** Two runs over the same
  HEAD counted 412,587 and 412,585 candidates (git prunes the walk heuristically when it
  meets commits older than the bound); the surviving instances were identical. A future
  version should pin the range by commit (`<sha>..HEAD`) instead of by date.
- **Patch phase parallelised** with 8 threads of read-only git calls; results are
  deterministic (ordered map), so output does not depend on scheduling.

## 2026-09-05 — more repositories

Survey (git-side funnel only, instances = 1–5 gold files; issue repos since 2024-01-01,
`Fixes:`-trailer repos since 2022-01-01):

| Repository | Link type | Instances | Decision |
|---|---|---:|---|
| qemu/qemu | `Fixes: <sha>` trailer | 2,367 | added (`qemu`), same rules as Linux |
| postgres/postgres | `Reported-by:` / `Bug: #N` + `Discussion:` URL | 1,333 | added (`postgres`), commit-message source |
| systemd/systemd | GitHub issues | 754 (since 2024) | added (`systemd`), run since 2022 |
| duckdb/duckdb | GitHub issues | 376 | skipped: links live in PR merge commits |
| nodejs/node | `Fixes: <issue url>` | 304 | skipped: most fixes are JavaScript-only |
| godotengine/godot | GitHub issues | 222 | skipped: links live in PR merge commits |
| sqlite/sqlite | Fossil mirror, forum posts | n/a | skipped: no API, 149 C files in `src/` |
| ClickHouse/ClickHouse | GitHub issues | pending clone | decided when the clone lands |

- **PostgreSQL candidates** are commits with a `Reported-by:` or `Bug: #N` trailer, which
  the project uses only for reported problems; `Discussion:` alone marks every commit and
  is not used as a signal. `metadata.references` holds the bug numbers and the
  `Discussion:` archive URLs. `Discussion`, `Backpatch-through`, `Author` and `Security`
  were added to the trailer keys so they are stripped from problem statements.
- Skipped repositories cost one table line to add later; the merge-commit-only link
  pattern (DuckDB, Godot) would need a "walk PR merges and take the PR's commits" rule
  that does not exist yet.
