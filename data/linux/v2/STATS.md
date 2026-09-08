# linux extraction stats

| Stage | Survived | % of candidates | Dropped here |
|---|---:|---:|---:|
| candidates | 412585 | 100.0% | 0 |
| not merge | 379555 | 92.0% | 33030 |
| not revert | 377187 | 91.4% | 2368 |
| has reference | 73087 | 17.7% | 304100 |
| has gold files | 63671 | 15.4% | 9416 |
| 1-5 gold files | 63115 | 15.3% | 556 |

## Run

- **instances written**: 63115
- **files**: instances-000.jsonl, instances-001.jsonl, instances-002.jsonl, instances-003.jsonl, instances-004.jsonl
- **with a report / without**: 5424 / 57691
- **instances with at least one report ref, per kind**: {'link': 42561, 'lore_report': 3853, 'syzbot': 1812, 'kernel_bugzilla': 548}
- **reports by source**: {'syzbot': 1809, 'lore_report': 3087, 'kernel_bugzilla': 528}
- **report drops**: {'lore_report: target is a patch': 230, 'lore_report: not found': 124, 'syzbot: not found': 4}
- **report counters (not drops)**: {'lore_report: charset fallback': 24}
- **problem statement names a gold path / basename / patched function**: over 5424 instances: path: 2995 (55.2%), basename: 3081 (56.8%), function: 2447 (45.1%)
- **commit message names a gold path / basename / patched function**: over 63115 instances: path: 4034 (6.4%), basename: 5450 (8.6%), function: 24887 (39.4%)
- **upstream**: torvalds/linux
- **upstream HEAD**: 654ae5d73c05bd2943d65636ce6cd0aa46e62f18
- **since**: 2022-01-01
- **extractor commit**: 7b845275553240afd002bb65582a65857970bef5
- **extractor version**: 0.2.1
- **report sources (resolution order)**: syzbot, lore_report, kernel_bugzilla
- **github token**: none
