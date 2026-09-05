"""Instance schema: one record per line of ``instances.jsonl``."""

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime

_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_REQUIRED_STR = (
    "instance_id",
    "repo",
    "base_commit",
    "fix_commit",
    "created_at",
    "problem_statement",
    "problem_source",
    "patch",
)


@dataclass
class Instance:
    instance_id: str
    repo: str
    base_commit: str
    fix_commit: str
    created_at: str
    problem_statement: str
    problem_source: str
    gold_files: list[str]
    gold_functions: list[str] | None
    patch: str
    metadata: dict = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)

    @classmethod
    def from_json(cls, line: str) -> Instance:
        return cls(**json.loads(line))

    def validate(self) -> list[str]:
        """Return a list of problems; empty means the instance is valid."""
        errors = []
        for name in _REQUIRED_STR:
            value = getattr(self, name)
            if not isinstance(value, str) or not value:
                errors.append(f"{name}: required non-empty string")
        for name in ("base_commit", "fix_commit"):
            if not _SHA_RE.match(getattr(self, name) or ""):
                errors.append(f"{name}: not a full 40-char lowercase SHA")
        try:
            datetime.fromisoformat(self.created_at)
        except TypeError, ValueError:
            errors.append("created_at: not ISO-8601")
        if not isinstance(self.gold_files, list) or not self.gold_files:
            errors.append("gold_files: must be a non-empty list")
        elif not all(isinstance(p, str) and p for p in self.gold_files):
            errors.append("gold_files: entries must be non-empty strings")
        if self.gold_functions is not None and not isinstance(self.gold_functions, list):
            errors.append("gold_functions: must be a list or null")
        if not isinstance(self.metadata, dict):
            errors.append("metadata: must be an object")
        return errors
