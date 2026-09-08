# clickhouse extraction stats

| Stage | Survived | % of candidates | Dropped here |
|---|---:|---:|---:|
| candidates | 198026 | 100.0% | 0 |
| not merge | 132697 | 67.0% | 65329 |
| not revert | 130561 | 65.9% | 2136 |
| has reference | 1497 | 0.8% | 129064 |
| has gold files | 1120 | 0.6% | 377 |
| 1-5 gold files | 1049 | 0.5% | 71 |

## Run

- **instances written**: 1049
- **files**: instances.jsonl
- **with a report / without**: 1022 / 27
- **dataset.jsonl rows (with a report, without patch)**: 1022
- **instances with at least one report ref, per kind**: {'github_issue': 1049}
- **reports by source**: {'github_issue': 1022}
- **report drops**: {'github_issue: reference is a pull request': 29}
- **report counters (not drops)**: {}
- **report kind (lore_report only)**: {}
- **report pick (pgsql_archive only)**: {}
- **reports shorter than 300 characters, per source**: {'github_issue': 12}
- **problem statement names a gold path / basename / patched function**: over 1022 instances: path: 399 (39.0%), basename: 431 (42.2%), function: 282 (27.6%)
- **commit message names a gold path / basename / patched function**: over 1049 instances: path: 23 (2.2%), basename: 63 (6.0%), function: 441 (42.0%)
- **upstream**: ClickHouse/ClickHouse
- **upstream HEAD**: d1adb9f9ffeeb41f2a7b4db2259d14e3db5a8edc
- **since**: 2022-01-01
- **extractor commit**: 7c02155cd52755aba95f521ee0b1b57cacc15458
- **extractor version**: 0.3.0
- **report sources (resolution order)**: github_issue
- **github token**: none
