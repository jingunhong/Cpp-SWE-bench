# postgres extraction stats

| Stage | Survived | % of candidates | Dropped here |
|---|---:|---:|---:|
| candidates | 12540 | 100.0% | 0 |
| not merge | 12540 | 100.0% | 0 |
| not revert | 12377 | 98.7% | 163 |
| has reference | 2069 | 16.5% | 10308 |
| has gold files | 1395 | 11.1% | 674 |
| 1-5 gold files | 1333 | 10.6% | 62 |

## Run

- **instances written**: 1333
- **files**: instances.jsonl
- **with a report / without**: 1318 / 15
- **instances with at least one report ref, per kind**: {'pgsql_archive': 1329, 'pgsql_bug': 135}
- **reports by source**: {'pgsql_archive': 1318}
- **report drops**: {'pgsql_archive: not found': 11}
- **report counters (not drops)**: {}
- **report kind (lore_report only)**: {}
- **report pick (pgsql_archive only)**: {'linked_message': 1038, 'bug_subject': 210, 'committers_reply': 70}
- **reports shorter than 300 characters, per source**: {'pgsql_archive': 48}
- **problem statement names a gold path / basename / patched function**: over 1318 instances: path: 180 (13.7%), basename: 432 (32.8%), function: 480 (36.4%)
- **commit message names a gold path / basename / patched function**: over 1333 instances: path: 2 (0.2%), basename: 117 (8.8%), function: 483 (36.2%)
- **upstream**: postgres/postgres
- **upstream HEAD**: 798bdcae89debabc59fa8afc6d690fec584db32f
- **since**: 2022-01-01
- **extractor commit**: 3dc0c6517b890e59a174565c31e5cdacb563c2c7
- **extractor version**: 0.2.1
- **report sources (resolution order)**: pgsql_archive
- **github token**: none
