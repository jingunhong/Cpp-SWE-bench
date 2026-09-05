# QEMU extraction (v0)

Upstream: `qemu/qemu` (GitHub mirror of gitlab.com/qemu-project/qemu), blob-less clone at
`repos/qemu`. QEMU follows the kernel's `Fixes: <sha> ("subject")` convention, so the
pipeline is the Linux one unchanged: candidates are non-merge, non-revert commits with a
`Fixes:` trailer; problem statement is the commit message with trailers stripped
(`problem_source = "commit_message"`); `metadata.references` holds the referenced SHA
prefixes. QEMU also uses `Resolves: <gitlab issue url>` lines; those are stripped as
trailers and not used as a candidate signal in v0.

## Results (`--since 2022-01-01`, `data/qemu/v0/STATS.md`)

40,309 candidates → 38,021 non-merge → 37,840 non-revert → 2,889 with a `Fixes:` trailer →
2,383 with gold files → **2,367 instances** (1–5 gold files). All validate; one 6.4 MB
file. Leakage over the full set: path 8.8%, basename 11.0%, patched function 31.6%.

## Caveats

- Only 7% of QEMU commits carry `Fixes:`; many fixes reference a GitLab issue instead
  (`Resolves: https://gitlab.com/qemu-project/qemu/-/issues/N`). Reading GitLab issues
  would roughly double the candidate pool and is the obvious next step for this repository.
