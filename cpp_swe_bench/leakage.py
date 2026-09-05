"""Leakage flags: does the problem statement name, verbatim, what the fix touched?"""

import re

_HUNK_FUNC_RE = re.compile(r"^@@ .* @@.*?\b([A-Za-z_]\w*)\s*\(", re.MULTILINE)
_KEYWORDS = frozenset({"if", "for", "while", "switch", "return", "sizeof", "defined", "else"})
FLAGS = ("path", "basename", "function")


def patched_functions(patch: str) -> set[str]:
    """Function names from the diff's hunk headers (git's default C/C++ funcname lines)."""
    return {f for f in _HUNK_FUNC_RE.findall(patch) if f not in _KEYWORDS}


def flags(statement: str, gold_files: list[str], patch: str) -> dict[str, bool]:
    """Whether ``statement`` contains a gold path, a gold basename, or a patched function."""
    funcs = patched_functions(patch)
    return {
        "path": any(g in statement for g in gold_files),
        "basename": any(g.rsplit("/", 1)[-1] in statement for g in gold_files),
        "function": any(re.search(rf"\b{re.escape(f)}\b", statement) for f in funcs),
    }
