# PostgreSQL extraction (v0)

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
- Bug report bodies from the `pgsql-bugs` archive are not fetched; the `Discussion:` URL
  is kept for a later version.
