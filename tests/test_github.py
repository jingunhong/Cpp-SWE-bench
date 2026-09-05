import json
from pathlib import Path

from cpp_swe_bench import github, gitutil


def make_issues(tmp_path: Path, responses: dict[int, dict | None]) -> github.Issues:
    issues = github.Issues("o/r", tmp_path / "cache", token=None)
    issues.calls = []
    issues._fetch = lambda n: (issues.calls.append(n), responses[n])[1]  # no network
    return issues


def test_cache_hits_disk_including_not_found(tmp_path: Path):
    issues = make_issues(tmp_path, {1: {"title": "t", "body": "b", "html_url": "u"}, 2: None})
    assert issues.get(1)["title"] == "t"
    assert issues.get(2) is None
    assert issues.get(1) and issues.get(2) is None
    assert issues.calls == [1, 2]
    assert json.loads((tmp_path / "cache/o__r/2.json").read_text()) is None


def test_issue_problem_skips_prs_and_missing(tmp_path: Path):
    issues = make_issues(
        tmp_path,
        {
            7: {"title": "PR", "body": "", "html_url": "u7", "pull_request": {}},
            8: None,
            9: {"title": " Crash ", "body": " when x \n", "html_url": "u9"},
        },
    )
    problem = github.IssueProblem(issues)
    msg = "fix\n\nFixes #7, closes #8, fixes #9"
    commit = gitutil.Commit("a", ["b"], "2024-01-01T00:00:00Z", msg, [])
    assert problem(commit) == (
        "Crash\n\nwhen x",
        "github_issue",
        {"issue_number": 9, "issue_url": "u9"},
    )
    assert problem(gitutil.Commit("a", ["b"], "d", "Fixes #7", [])) is None
    assert problem.drops == {"reference is a pull request": 2, "issue not found": 1}
