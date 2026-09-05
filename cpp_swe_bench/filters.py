"""Pure filter functions applied to mined commits."""

import re

CPP_SUFFIXES = frozenset({".c", ".h", ".cc", ".cpp", ".cxx", ".hh", ".hpp", ".hxx"})
_TEST_DIRS = frozenset({"test", "tests", "testing", "selftests", "unittest", "unittests"})
_TEST_FILE_RE = re.compile(r"(^|[_.-])tests?([_.-]|$)", re.IGNORECASE)
_REVERT_RE = re.compile(r"^Revert\b|^\s*This reverts commit\b", re.MULTILINE)
_TRAILER_KEYS = {
    "signed-off-by",
    "reviewed-by",
    "acked-by",
    "tested-by",
    "reported-by",
    "suggested-by",
    "co-developed-by",
    "co-authored-by",
    "cc",
    "link",
    "fixes",
    "closes",
    "resolves",
    "change-id",
    "reviewed-on",
    "message-id",
    "bug",
    "references",
    "see-also",
}
_TRAILER_RE = re.compile(r"^([A-Za-z][A-Za-z0-9-]*):[ \t]")
_FIXES_SHA_RE = re.compile(r"^Fixes:\s*([0-9a-f]{7,40})\b", re.IGNORECASE | re.MULTILINE)
_ISSUE_KEYWORDS = r"\b(?:fix|fixes|fixed|close|closes|closed|resolve|resolves|resolved)\s*:?\s*"
MIN_GOLD_FILES, MAX_GOLD_FILES = 1, 5


def is_cpp_source(path: str) -> bool:
    """True for C/C++ source or header files by extension."""
    dot = path.rfind(".")
    return dot > path.rfind("/") and path[dot:].lower() in CPP_SUFFIXES


def is_test_path(path: str) -> bool:
    """True if any directory component is a test directory (``tests/``, ``selftests/``,
    ``tools/testing/``...) or the file name carries a ``test`` token (``foo_test.c``,
    ``test-foo.c``, ``foo.test.cc``)."""
    parts = path.lower().split("/")
    return any(p in _TEST_DIRS for p in parts[:-1]) or bool(_TEST_FILE_RE.search(parts[-1]))


def is_merge(parents: list[str]) -> bool:
    """True for commits with more than one parent."""
    return len(parents) > 1


def is_revert(message: str) -> bool:
    """True if the subject starts with ``Revert`` or the body says ``This reverts commit``."""
    return bool(_REVERT_RE.search(message))


def gold_files(paths: list[str]) -> list[str]:
    """Changed paths that count as gold: non-test C/C++ sources, sorted."""
    return sorted(p for p in paths if is_cpp_source(p) and not is_test_path(p))


def file_count_ok(paths: list[str]) -> bool:
    """Gate on the number of gold files (inclusive bounds)."""
    return MIN_GOLD_FILES <= len(paths) <= MAX_GOLD_FILES


def is_trailer(line: str) -> bool:
    m = _TRAILER_RE.match(line)
    return bool(m) and (m[1].lower() in _TRAILER_KEYS or m[1].lower().endswith("-by"))


def strip_trailers(message: str) -> str:
    """Drop trailer lines (``Signed-off-by:``, ``Fixes:``, ``Link:``, any ``*-by:`` ...)
    anywhere in the message and collapse the leftover blank lines."""
    kept = [line.rstrip() for line in message.splitlines() if not is_trailer(line)]
    text = "\n".join(kept)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def fixes_shas(message: str) -> list[str]:
    """SHA prefixes referenced by ``Fixes: <sha> (...)`` trailers, in order."""
    return _FIXES_SHA_RE.findall(message)


def issue_refs(message: str, upstream: str) -> list[int]:
    """Issue numbers of ``upstream`` (``owner/repo``) referenced as ``Fixes #N``,
    ``Closes: #N``, ``Resolves <issue url>``, ``Fix owner/repo#N``... in order of first
    mention, without duplicates. References to other repositories are ignored."""
    up = re.escape(upstream)
    pattern = _ISSUE_KEYWORDS + rf"(?:https://github\.com/{up}/issues/|{up}#|#)(\d+)\b"
    return list(dict.fromkeys(int(n) for n in re.findall(pattern, message, re.IGNORECASE)))
