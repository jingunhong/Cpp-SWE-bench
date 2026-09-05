# systemd extraction stats

| Stage | Survived | % of candidates | Dropped here |
|---|---:|---:|---:|
| candidates | 36174 | 100.0% | 0 |
| not merge | 31169 | 86.2% | 5005 |
| not revert | 30936 | 85.5% | 233 |
| has reference | 2055 | 5.7% | 28881 |
| has gold files | 1498 | 4.1% | 557 |
| 1-5 gold files | 1424 | 3.9% | 74 |
| has problem statement | 1418 | 3.9% | 6 |

## Run

- **instances written**: 1418
- **files**: instances.jsonl
- **problem statement names a gold path / basename / patched function**: path: 282 (19.9%), basename: 314 (22.1%), function: 225 (15.9%)
- **upstream**: systemd/systemd
- **upstream HEAD**: 726e17a933296e7107f862c6ebe175a3d176e6bb
- **since**: 2022-01-01
- **extractor commit**: 4c23dfef71d5169d1898427ec8f2a8b36d6d42e8
- **extractor version**: 0.1.0
- **problem source**: github_issue
- **problem statement drops**: {'reference is a pull request': 7}
- **github token**: GITHUB_TOKEN
