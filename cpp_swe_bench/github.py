"""GitHub issue fetcher: stdlib HTTP, on-disk cache, polite rate limiting."""

import http.client
import json
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

from . import filters, gitutil

API = "https://api.github.com"


class Issues:
    """Fetch ``/repos/<upstream>/issues/<n>`` with a JSON cache under ``cache_dir``.

    Without a token GitHub allows 60 requests/hour, so unauthenticated runs pause a
    second between calls and sleep until the reset time when the quota is exhausted.
    """

    def __init__(self, upstream: str, cache_dir: Path, token: str | None):
        self.upstream, self.token = upstream, token
        self.dir = cache_dir / upstream.replace("/", "__")
        self.dir.mkdir(parents=True, exist_ok=True)

    def get(self, number: int) -> dict | None:
        """Issue JSON, or None when the number does not exist. Cached either way."""
        path = self.dir / f"{number}.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        data = self._fetch(number)
        path.write_text(json.dumps(data), encoding="utf-8")
        return data

    def _fetch(self, number: int) -> dict | None:
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "cpp-swe-bench"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        url = f"{API}/repos/{self.upstream}/issues/{number}"
        req = urllib.request.Request(url, headers=headers)
        for attempt in range(8):
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    self._pace(resp.headers)
                    return json.load(resp)
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    return None
                if e.code in (403, 429):
                    self._pace(e.headers, exhausted=True)
                elif e.code >= 500:
                    time.sleep(2**attempt)
                else:
                    raise
            except urllib.error.URLError, http.client.HTTPException, TimeoutError:
                time.sleep(2**attempt)  # transient network error, retry with backoff
        raise RuntimeError(f"giving up on issue {number} after 8 attempts")

    def _pace(self, headers, exhausted: bool = False) -> None:
        remaining = int(headers.get("X-RateLimit-Remaining", "1"))
        if exhausted or remaining == 0:
            reset = int(headers.get("X-RateLimit-Reset", "0"))
            time.sleep(max(reset - time.time(), 60))
        elif not self.token:
            time.sleep(1)


class IssueProblem:
    """``problem`` callback for :func:`cpp_swe_bench.extract.mine`: title + body of the
    first referenced number that is a real issue (not a pull request, not deleted)."""

    def __init__(self, issues: Issues):
        self.issues = issues
        self.drops: Counter[str] = Counter()

    def __call__(self, c: gitutil.Commit) -> tuple[str, str, dict] | None:
        for number in filters.issue_refs(c.message, self.issues.upstream):
            issue = self.issues.get(number)
            if issue is None:
                self.drops["issue not found"] += 1
            elif "pull_request" in issue:
                self.drops["reference is a pull request"] += 1
            elif not (issue.get("title") or "").strip():
                self.drops["issue has no title"] += 1
            else:
                text = f"{issue['title'].strip()}\n\n{(issue.get('body') or '').strip()}".strip()
                extra = {"issue_number": number, "issue_url": issue["html_url"]}
                return text, "github_issue", extra
        return None
