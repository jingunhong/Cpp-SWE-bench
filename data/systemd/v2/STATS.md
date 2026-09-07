# systemd extraction stats

| Stage | Survived | % of candidates | Dropped here |
|---|---:|---:|---:|
| candidates | 36174 | 100.0% | 0 |
| not merge | 31169 | 86.2% | 5005 |
| not revert | 30936 | 85.5% | 233 |
| has reference | 2055 | 5.7% | 28881 |
| has gold files | 1498 | 4.1% | 557 |
| 1-5 gold files | 1424 | 3.9% | 74 |

## Run

- **instances written**: 1424
- **files**: instances.jsonl
- **with a report / without**: 1418 / 6
- **instances with at least one report ref, per kind**: {'github_issue': 1424}
- **reports by source**: {'github_issue': 1418}
- **report drops**: {'github_issue: reference is a pull request': 7}
- **problem statement names a gold path / basename / patched function**: over 1418 instances: path: 282 (19.9%), basename: 314 (22.1%), function: 225 (15.9%)
- **commit message names a gold path / basename / patched function**: over 1424 instances: path: 14 (1.0%), basename: 24 (1.7%), function: 180 (12.6%)
- **upstream**: systemd/systemd
- **upstream HEAD**: 726e17a933296e7107f862c6ebe175a3d176e6bb
- **since**: 2022-01-01
- **extractor commit**: 8b10cebf08ddb952f23790fa0a12b3fad17dfb0f
- **extractor version**: 0.2.0
- **report sources (resolution order)**: github_issue
- **github token**: GITHUB_TOKEN
