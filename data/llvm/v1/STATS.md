# llvm extraction stats

| Stage | Survived | % of candidates | Dropped here |
|---|---:|---:|---:|
| candidates | 110841 | 100.0% | 0 |
| not merge | 110841 | 100.0% | 0 |
| not revert | 106646 | 96.2% | 4195 |
| has reference | 10085 | 9.1% | 96561 |
| has gold files | 9092 | 8.2% | 993 |
| 1-5 gold files | 8504 | 7.7% | 588 |
| has problem statement | 8357 | 7.5% | 147 |

## Run

- **instances written**: 8357
- **files**: instances-000.jsonl, instances-001.jsonl
- **problem statement names a gold path / basename / patched function**: path: 1239 (14.8%), basename: 1937 (23.2%), function: 1592 (19.0%)
- **upstream**: llvm/llvm-project
- **upstream HEAD**: 3efd20d463e1b1210d2ff07cd79b68d6fa215f24
- **since**: 2024-01-01
- **extractor commit**: 43038d819159ba0d86b25fc757dfb5b23ce78f2b
- **extractor version**: 0.1.0
- **problem source**: github_issue
- **problem statement drops**: {'reference is a pull request': 149, 'issue not found': 1}
- **github token**: GITHUB_TOKEN
