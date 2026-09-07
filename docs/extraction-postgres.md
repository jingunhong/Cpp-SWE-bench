# PostgreSQL extraction (v0, v2)

Upstream: `postgres/postgres` (GitHub mirror of git.postgresql.org), blob-less clone at
`repos/postgres`, walking `master` only, so back-patched copies of a fix on release branches
never appear. Candidates are non-revert commits carrying a `Reported-by:` or `Bug: #N`
trailer, the project's conventions for fixes of reported problems. The problem statement is
the commit message with trailers stripped (`problem_source = "commit_message"`);
PostgreSQL adds `Discussion:`, `Backpatch-through:`, `Author:` and `Security:` to the usual
keys. `metadata.references` holds the bug numbers (`#18123`) and the `Discussion:` mailing
list archive URLs, which point at the original report.

## Results (`--since 2022-01-01`, `data/postgres/v0/STATS.md`)

12,540 candidates (no merge commits) → 12,377 non-revert → 2,069 with a report trailer →
1,395 with gold files → **1,333 instances** (1–5 gold files). All validate; one 5.7 MB file.
Leakage over the full set: path 0.2%, basename 8.8%, patched function 36.2%.

## Caveats

- `Reported-by:` is also used for reported shortcomings that are not defects (a sampled
  instance adjusts query jumbling for a new command). The 143 commits with an explicit
  `Bug: #N` number are the strict subset; filter on `metadata.references` starting with `#`.
- PostgreSQL commit messages describe the fix as much as the problem, so leakage of the
  patched function name is high (36%), comparable to Linux.
- Bug report bodies from the `pgsql-bugs` archive are not fetched in v0; v2 does.

## v2: mailing-list reports as problem statements

`data/postgres/v2/` (same clone, HEAD, range and funnel as v0: 1,333 instances). The
`Discussion:` URL of each commit is resolved through the archive's flat thread view
(`https://www.postgresql.org/message-id/flat/<msgid>`; the raw-message endpoint and
`postgr.es/m/` redirect non-browser clients to HTML, so the page is parsed). In the thread
the first message whose subject starts with `BUG #` is the report; otherwise the thread's
first message is. `problem_statement` = subject + body with `>`-quoted lines and the
`-- ` signature removed (`problem_source = "pgsql_archive"`, `metadata.report_url` is the
chosen message); the commit message moved to `commit_message`.

### Reports

| | Instances |
|---|---:|
| with a `Discussion:` archive URL | 1,329 (99.7%) |
| resolved to a message | 1,318 |
| `pgsql_archive: not found` (404 on the archive) | 11 refs |
| with `problem_statement: null` | 15 (1.1%) |
| report subject starts with `BUG #` | 210 |
| `Bug: #N` trailer (recorded in `report_refs.pgsql_bug`) | 135 |

Leakage: `problem_statement` (1,318) path 13.4%, basename 27.2%, patched function 25.3%;
`commit_message` (1,333) path 0.2%, basename 8.8%, function 36.2%. Reports name files
more often than the commit message (backtraces, `psql` output) and the patched function
less often. Report length: median 1,828 characters, longest 134k (a review thread whose
root message carries a long analysis).

Caveats: a `Discussion:` link into a `pgsql-hackers` thread yields that thread's first
message, which is a report of a shortcoming or a design discussion rather than a bug
report (`Reported-by:` marks both); the `BUG #` subset is the strict one. The archive
obfuscates addresses (`name(at)host(dot)org`) and that text is kept as is. All 1,333
validate; one 9.9 MB file.
