# dependencies.py
from dataclasses import dataclass, field

@dataclass
class ApplicationStore:
    applications: list[dict] = field(default_factory=list)
    next_id: int = 1

_store = ApplicationStore()


def get_store() -> ApplicationStore:
    return _store