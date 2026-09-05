from pathlib import Path

from cpp_swe_bench import extract, filters, gitutil, writers
from cpp_swe_bench.schema import Instance


def test_end_to_end(synthetic_repo, tmp_path: Path):
    repo, shas = synthetic_repo
    funnel: dict[str, int] = {}
    instances = list(
        extract.mine(
            repo,
            "toy",
            "example/toy",
            since=None,
            references=filters.fixes_shas,
            problem=extract.commit_message_problem,
            funnel=funnel,
        )
    )
    assert funnel == {
        "candidates": 5,
        "not merge": 5,
        "not revert": 4,
        "has reference": 3,
        "has gold files": 2,
        "1-5 gold files": 1,
        "has problem statement": 1,
    }
    [inst] = instances
    assert inst.instance_id == f"toy__{shas['fix'][:12]}"
    assert inst.base_commit == shas["initial"]
    assert inst.fix_commit == shas["fix"]
    assert inst.created_at == "2023-02-01T10:00:00+09:00"
    assert inst.problem_statement == "foo: fix off-by-one\n\nfoo() returned the wrong value."
    assert inst.gold_files == ["drivers/foo.c", "drivers/foo.h"]
    assert inst.gold_functions is None
    assert inst.metadata["references"] == [shas["initial"][:12]]

    extract.add_patches(repo, instances)
    assert "return 0" in inst.patch and "+int foo(void);" in inst.patch
    assert inst.validate() == []

    out = tmp_path / "instances.jsonl"
    assert writers.write_jsonl(out, instances) == 1
    assert Instance.from_json(out.read_text().splitlines()[0]) == inst
    stats = tmp_path / "STATS.md"
    writers.write_stats(stats, "t", list(funnel.items()), {"n": 1})
    assert "| 1-5 gold files | 1 | 20.0% | 1 |" in stats.read_text()


def test_gitutil_helpers(synthetic_repo):
    repo, shas = synthetic_repo
    assert gitutil.parents(repo, shas["fix"]) == [shas["initial"]]
    assert gitutil.changed_files(repo, shas["initial"], shas["fix"]) == [
        "drivers/foo.c",
        "drivers/foo.h",
    ]
    assert gitutil.author_date(repo, shas["fix"]) == "2023-02-01T10:00:00+09:00"
    assert gitutil.message(repo, shas["fix"]).startswith("foo: fix off-by-one\n")
    assert len(gitutil.blob_oids(repo, shas["initial"], shas["fix"], ["drivers/foo.c"])) == 2
    assert gitutil.head(repo) == shas["too_many"]
