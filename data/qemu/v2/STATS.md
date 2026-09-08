# qemu extraction stats

| Stage | Survived | % of candidates | Dropped here |
|---|---:|---:|---:|
| candidates | 40309 | 100.0% | 0 |
| not merge | 38021 | 94.3% | 2288 |
| not revert | 37840 | 93.9% | 181 |
| has reference | 3503 | 8.7% | 34337 |
| has gold files | 2856 | 7.1% | 647 |
| 1-5 gold files | 2821 | 7.0% | 35 |

## Run

- **instances written**: 2821
- **files**: instances.jsonl
- **with a report / without**: 677 / 2144
- **dataset.jsonl rows (with a report, without patch)**: 677
- **instances with at least one report ref, per kind**: {'gitlab_issue': 683, 'link': 294, 'launchpad': 6}
- **reports by source**: {'gitlab_issue': 677}
- **report drops**: {'gitlab_issue: not found': 8}
- **report counters (not drops)**: {}
- **report kind (lore_report only)**: {}
- **report pick (pgsql_archive only)**: {}
- **reports shorter than 300 characters, per source**: {'gitlab_issue': 15}
- **problem statement names a gold path / basename / patched function**: over 677 instances: path: 271 (40.0%), basename: 297 (43.9%), function: 179 (26.4%)
- **commit message names a gold path / basename / patched function**: over 2821 instances: path: 246 (8.7%), basename: 310 (11.0%), function: 866 (30.7%)
- **upstream**: qemu/qemu
- **upstream HEAD**: ff1d2d19d7e24893e2012d879f8e73077e17b9bd
- **since**: 2022-01-01
- **extractor commit**: 7c02155cd52755aba95f521ee0b1b57cacc15458
- **extractor version**: 0.3.0
- **report sources (resolution order)**: gitlab_issue
- **github token**: none
