# Linux extraction (v0)

Upstream: `torvalds/linux`, blob-less clone at `repos/linux`. Candidates are non-merge,
non-revert commits whose message carries a `Fixes: <sha> ("...")` trailer. The problem
statement is the commit subject and body with trailers stripped (`problem_source =
"commit_message"`); `base_commit` is the first parent; `created_at` is the author date;
`gold_files` are the changed non-test C/C++ sources; `gold_functions` is `null`.

## Range

`--since 2026-01-01` (committer date), upstream HEAD and exact command in
`data/linux/v0/COMMAND.txt`. The full range since 2022 was measured first with `--no-patch`
and is far over the 50 MB file limit, so v0 keeps the most recent eight months. See
`docs/decisions.md`.

Reference funnel for `--since 2022-01-01` (dry run, not shipped):

| Stage | Survived | % of candidates |
|---|---:|---:|
| candidates | 412,587 | 100.0% |
| not merge | 379,557 | 92.0% |
| not revert | 377,189 | 91.4% |
| has `Fixes:` reference | 73,088 | 17.7% |
| has gold files | 63,671 | 15.4% |
| 1–5 gold files | 63,115 | 15.3% |
| has problem statement | 63,115 | 15.3% |

Shipped v0 funnel (`--since 2026-01-01`, `data/linux/v0/STATS.md`): 66,410 candidates →
60,927 non-merge → 60,625 non-revert → 16,577 with a `Fixes:` reference → 15,042 with gold
files → **14,918 instances** (1–5 gold files). `scripts/validate.py`: 14,918 valid, 0 invalid,
0 duplicate ids. `instances.jsonl` is 43.7 MB.

## Practical notes

- A name-only `git log` over the whole range is tree-only on a partial clone (verified:
  no promisor pack appeared over 412k commits). Patches need blobs: the extractor collects
  pre/post blob ids with `git diff-tree` and bulk-fetches them in batches of 5,000 before
  running `git diff`, which then works offline at ~30 ms per instance.
- Keep shells, editors and IDE git integrations out of `repos/linux`; anything that diffs
  HEAD against the (empty, `--no-checkout`) index fetches all ~96k blobs of HEAD (293 MB).
- `gc.auto` is set to 0 on the clone; a background repack of the 2 GB clone stalls diffs.

## Leakage note

`uv run python scripts/leakage.py data/linux/v0/instances.jsonl --n 20 --seed 0` samples 20
instances and checks whether the problem statement contains, verbatim, a gold file path,
a gold file basename, or a function name taken from the patch's hunk headers.

| Named verbatim in the problem statement | Instances (of 20) |
|---|---:|
| full gold file path | 2 |
| gold file basename | 3 |
| function name from the patch | 9 |

Function names leak in roughly half the sample: kernel commit subjects are conventionally
`subsystem: function_name: what was wrong`, and bodies routinely quote the function being
fixed. Paths are rarer. Nothing is scrubbed in v0; a later version should at least measure
this on the full set and consider masking identifiers or evaluating on the body only.
