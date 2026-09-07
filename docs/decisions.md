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
| ClickHouse/ClickHouse | GitHub issues | 954 | added (`clickhouse`), run since 2022; blob-less clone is 6.7 GB |

- **PostgreSQL candidates** are commits with a `Reported-by:` or `Bug: #N` trailer, which
  the project uses only for reported problems; `Discussion:` alone marks every commit and
  is not used as a signal. `metadata.references` holds the bug numbers and the
  `Discussion:` archive URLs. `Discussion`, `Backpatch-through`, `Author` and `Security`
  were added to the trailer keys so they are stripped from problem statements.
- Skipped repositories cost one table line to add later; the merge-commit-only link
  pattern (DuckDB, Godot) would need a "walk PR merges and take the PR's commits" rule
  that does not exist yet.

## 2026-09-07 — v2: original reports as problem statements

- **Schema.** `problem_statement` holds the original report only and is `null` when none
  is linked or none resolves; `problem_source` is `null` exactly then. The old commit-message
  text moves to a new top-level `commit_message` (always present). `problem_source` values:
  `github_issue`, `gitlab_issue`, `syzbot`, `lore_report`, `kernel_bugzilla`, `pgsql_archive`.
  `metadata.leakage` is computed against `problem_statement` (`null` without one);
  `metadata.commit_message_leakage` against `commit_message`. Never mixed. Instances without
  a report are kept; the `has problem statement` funnel stage is gone. `extractor_version`
  0.2.0, output under `data/<repo>/v2/`, v0/v1 untouched.
- **No fallback, no invented source.** `commit_message` is never copied into
  `problem_statement`; what consumers do at training time is their decision.
- **`commit_message` is required non-empty** by `validate()`. No instance in any run so far
  had an empty stripped message; if one appears, validation flags it rather than the
  pipeline silently keeping or dropping it.
- **`metadata.report_refs`** is a dict keyed by kind (source name, or `link`/`launchpad`/
  `pgsql_bug` for kinds without a fetcher) so per-source yield can be measured offline; the
  refs are stored as parsed tokens the fetcher takes (URLs as written, `extid=<hash>` for
  syzbot, issue numbers as strings for GitHub, `#N` for PostgreSQL bug numbers).
- **One `Source` abstraction** (`cpp_swe_bench/reports.py`) replaces `github.py`: `refs`,
  `fetch` (raw, JSON-serialisable), `parse`; raw responses cached as JSON under
  `repos/cache/<source>/` (`null` for 404), shared retry/backoff and rate-limit sleeps.
  The existing GitHub caches were moved on disk to `repos/cache/github_issue/<owner__repo>/`
  so the issue-backed re-runs stay offline. Report fetching is a stage in `extract.py`
  after the git filters and before patches; `--no-reports` skips it.
- **Step 0 yield** (`--no-patch --no-reports`, same clones and ranges as v1/v0; instances
  with at least one ref of the kind):

  | Repository | Instances | Fetchable refs | Record-only refs |
  |---|---:|---|---|
  | linux (2022+) | 63,115 | lore `Closes:` 3,853; syzbot 1,812; bugzilla.kernel.org 548; any of the three 5,752 (9.1%) | `Link:` 42,561 |
  | qemu (2022+) | 2,821 (was 2,367: GitLab issue URLs are now a candidate signal) | GitLab issue 683 | `Link:` 294; Launchpad 6 |
  | postgres (2022+) | 1,333 | `Discussion:` archive URL 1,329 | `Bug: #N` 135 |
  | llvm (2024+) | 8,504 | GitHub issue 8,504 | |
  | systemd (2022+) | 1,424 | GitHub issue 1,424 | |
  | clickhouse (2022+) | 1,049 | GitHub issue 1,049 | |

  The issue-backed counts are before the PR/404 drops that used to happen at the
  `has problem statement` stage (llvm v1 8,357, systemd v0 1,418, clickhouse v0 1,022);
  those commits are now kept with `problem_statement: null`.
- **Launchpad fetcher skipped** (6 QEMU instances). Bugzilla is worth it (548).
- **Fetchers were written together with the parsers** (same module) but not run on any
  dataset before the yield above was committed; each was smoke-tested on two real refs.
- **`Link:` is recorded, never fetched.** Even when it points at lore it is usually the
  patch's own submission link.
- **syzbot and bugzilla URLs are taken from any line of the message**, not only from
  `Reported-by:`/`Closes:`: `syzkaller.appspot.com/bug?` and `bugzilla.kernel.org/show_bug.cgi`
  can only be bug pages, so a `Link:` to them is a report. lore URLs are taken from
  `Closes:` only.
- **lore targets whose subject is a `[PATCH ...]` post** are counted as a drop
  (`lore_report: target is a patch`) instead of becoming the problem statement: a
  `Closes:` pointing at a patch submission is not a report. `Re: [PATCH ...]` replies are
  kept: in the first 1,164 cached lore targets 292 were such replies (a reviewer or bot
  reporting a problem against a posted patch) versus 89 bare patch posts. Mail bodies drop `>`-quoted
  lines and everything from a `-- ` signature marker; kernel test robot reports keep
  their build logs.
- **PostgreSQL archive: the flat thread page is the source.** `/message-id/raw/` and
  `postgr.es/m/` redirect non-browser clients to the HTML view, so one request fetches
  `/message-id/flat/<msgid>` and the messages are parsed from its HTML (subject,
  message-id, `message-content` div). The message whose subject starts with `BUG #` wins,
  else the thread's first message. The archive obfuscates addresses (`(at)`, `(dot)`);
  that text is kept as is. `Bug: #N` alone is not fetchable (no number-to-message mapping)
  and stays in `report_refs`.
- **GitLab issue URLs are the QEMU report ref wherever they appear** (`Resolves:`,
  `Fixes:`, `Closes:`, `Buglink:`, `Bug:`); GitLab's `web_url` (which now points at
  `-/work_items/N`) is stored as `report_url`.
- **Bugzilla private bugs** (HTTP 401) are cached as `null` like 404s.
- **Raw text responses are decoded as UTF-8 with replacement** before caching; mail in
  other charsets (rare on lore) may carry replacement characters.
- **syzbot bugs behind a login** (some namespaces redirect `bug?extid=` to a Google sign-in
  page instead of returning JSON) are cached as `null` and counted as
  `syzbot: not found`. The first Linux v2 run lost its syzbot thread to this after 104
  bugs; the cache made the restart free.
- **Report caches are warmed one thread per source** (`extract.warm_caches`) before the
  sequential resolution, so the three Linux hosts are fetched concurrently; this fetches a
  few refs the resolution order would have skipped, which only fills the cache.

## 2026-09-07 — v2 results

| Dataset | Instances | With a report | Sources | Drops (refs) |
|---|---:|---:|---|---|
| linux v2 | 63,115 | 5,424 (8.6%) | syzbot 1,809; lore 3,087; bugzilla 528 | lore: 230 patch posts, 124 not found; syzbot: 4 not found |
| qemu v2 | 2,821 | 677 (24.0%) | gitlab_issue | 8 not found |
| postgres v2 | 1,333 | 1,318 (98.9%) | pgsql_archive | 11 not found |
| llvm v2 | 8,504 | 8,357 (98.3%) | github_issue | 149 pull requests, 1 not found |
| systemd v2 | 1,424 | 1,418 (99.6%) | github_issue | 7 pull requests |
| clickhouse v2 | 1,049 | 1,022 (97.4%) | github_issue | 29 pull requests |

- **Run order.** All six ran in parallel (different hosts and caches); Linux was restarted
  three times from its cache (syzbot login redirect, syzbot pacing, the `Re: [PATCH`
  rule), each restart free. Every output validates with 0 invalid and 0 duplicate ids.
- **Not done.** Launchpad fetcher (6 refs), PR-merge walking, `gold_functions`, masking,
  splits: out of scope as specified. `Bug: #N` without a `Discussion:` URL stays
  unresolved (4 PostgreSQL instances).
