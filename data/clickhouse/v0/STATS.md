# clickhouse extraction stats

| Stage | Survived | % of candidates | Dropped here |
|---|---:|---:|---:|
| candidates | 198025 | 100.0% | 0 |
| not merge | 132696 | 67.0% | 65329 |
| not revert | 130560 | 65.9% | 2136 |
| has reference | 1497 | 0.8% | 129063 |
| has gold files | 1120 | 0.6% | 377 |
| 1-5 gold files | 1049 | 0.5% | 71 |
| has problem statement | 1022 | 0.5% | 27 |

## Run

- **instances written**: 1022
- **files**: instances.jsonl
- **problem statement names a gold path / basename / patched function**: path: 399 (39.0%), basename: 431 (42.2%), function: 282 (27.6%)
- **upstream**: ClickHouse/ClickHouse
- **upstream HEAD**: d1adb9f9ffeeb41f2a7b4db2259d14e3db5a8edc
- **since**: 2022-01-01
- **extractor commit**: c0792c1c301313c4957a27e965de4412bc843ee9
- **extractor version**: 0.1.0
- **problem source**: github_issue
- **problem statement drops**: {'reference is a pull request': 29}
- **github token**: GITHUB_TOKEN
