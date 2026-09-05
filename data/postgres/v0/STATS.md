# postgres extraction stats

| Stage | Survived | % of candidates | Dropped here |
|---|---:|---:|---:|
| candidates | 12540 | 100.0% | 0 |
| not merge | 12540 | 100.0% | 0 |
| not revert | 12377 | 98.7% | 163 |
| has reference | 2069 | 16.5% | 10308 |
| has gold files | 1395 | 11.1% | 674 |
| 1-5 gold files | 1333 | 10.6% | 62 |
| has problem statement | 1333 | 10.6% | 0 |

## Run

- **instances written**: 1333
- **files**: instances.jsonl
- **problem statement names a gold path / basename / patched function**: path: 2 (0.2%), basename: 117 (8.8%), function: 483 (36.2%)
- **upstream**: postgres/postgres
- **upstream HEAD**: 798bdcae89debabc59fa8afc6d690fec584db32f
- **since**: 2022-01-01
- **extractor commit**: 4c23dfef71d5169d1898427ec8f2a8b36d6d42e8
- **extractor version**: 0.1.0
- **problem source**: commit_message
- **problem statement drops**: {}
- **github token**: none
