import datetime
from dataclasses import dataclass, field
from typing import Optional, List

from domain.diff import Patch


@dataclass
class Worklog:
    task_code: str
    brief: str
    logs: List[str] = field(default_factory=lambda: [])
    project_id: Optional[int] = field(default_factory=lambda: None)
    time_spent_seconds: int = field(default_factory=lambda: 0)
    time_start: datetime.datetime = field(default_factory=lambda: None)
    patches: List[Patch] = field(default_factory=lambda: [])
