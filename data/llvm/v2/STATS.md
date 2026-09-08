# llvm extraction stats

| Stage | Survived | % of candidates | Dropped here |
|---|---:|---:|---:|
| candidates | 110841 | 100.0% | 0 |
| not merge | 110841 | 100.0% | 0 |
| not revert | 106646 | 96.2% | 4195 |
| has reference | 10085 | 9.1% | 96561 |
| has gold files | 9092 | 8.2% | 993 |
| 1-5 gold files | 8504 | 7.7% | 588 |

## Run

- **instances written**: 8504
- **files**: instances-000.jsonl, instances-001.jsonl
- **with a report / without**: 8357 / 147
- **dataset.jsonl rows (with a report, without patch)**: 8357
- **instances with at least one report ref, per kind**: {'github_issue': 8504}
- **reports by source**: {'github_issue': 8357}
- **report drops**: {'github_issue: reference is a pull request': 149, 'github_issue: not found': 1}
- **report counters (not drops)**: {}
- **report kind (lore_report only)**: {}
- **report pick (pgsql_archive only)**: {}
- **reports shorter than 300 characters, per source**: {'github_issue': 563}
- **problem statement names a gold path / basename / patched function**: over 8357 instances: path: 1239 (14.8%), basename: 1937 (23.2%), function: 1592 (19.0%)
- **commit message names a gold path / basename / patched function**: over 8504 instances: path: 99 (1.2%), basename: 304 (3.6%), function: 1547 (18.2%)
- **upstream**: llvm/llvm-project
- **upstream HEAD**: 3efd20d463e1b1210d2ff07cd79b68d6fa215f24
- **since**: 2024-01-01
- **extractor commit**: 7c02155cd52755aba95f521ee0b1b57cacc15458
- **extractor version**: 0.3.0
- **report sources (resolution order)**: github_issue
- **github token**: none
